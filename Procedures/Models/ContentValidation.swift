import Foundation

struct ContentValidationIssue: Identifiable, Hashable {
    enum Severity: String, Hashable {
        case blocker = "Blocker"
        case warning = "Warning"
        case polish = "Polish"
    }

    let id = UUID()
    let severity: Severity
    let procedureID: String?
    let procedureTitle: String?
    let message: String

    var displayMessage: String {
        if let procedureTitle {
            return "\(procedureTitle): \(message)"
        }
        return message
    }
}

enum ContentValidator {
    static func validate(
        _ procedures: [Procedure],
        rescueCards: [ComplicationRescueCard] = [],
        kits: [Kit] = []
    ) -> [ContentValidationIssue] {
        var issues: [ContentValidationIssue] = []

        let ids = procedures.map(\.id)
        let duplicateIDs = Dictionary(grouping: ids, by: { $0 }).filter { $0.value.count > 1 }.keys.sorted()
        if !duplicateIDs.isEmpty {
            issues.append(.init(severity: .blocker, procedureID: nil, procedureTitle: nil, message: "Duplicate procedure IDs: \(duplicateIDs.joined(separator: ", "))."))
        }

        for procedure in procedures {
            issues.append(contentsOf: validate(procedure))
        }

        issues.append(contentsOf: validateRescueCards(rescueCards, procedureIDs: Set(ids)))
        issues.append(contentsOf: validateRescueCoverage(procedures, rescueCards: rescueCards))
        issues.append(contentsOf: validateKits(kits, procedureIDs: Set(ids)))

        // Dosing rescue linkage resolves against the loaded rescue cards, so it
        // lives here rather than in the per-procedure pass. Skip when no cards
        // were passed at all (unit fixtures) to avoid vacuous noise.
        if !rescueCards.isEmpty {
            let rescueIDs = Set(rescueCards.map(\.id))
            for procedure in procedures {
                if let rescueCardID = procedure.dosing?.rescueCardID, !rescueIDs.contains(rescueCardID) {
                    issues.append(.init(
                        severity: .blocker,
                        procedureID: procedure.id,
                        procedureTitle: procedure.title,
                        message: "dosing rescue card ID '\(rescueCardID)' not found in rescue_cards.json."
                    ))
                }
            }
        }

        // Aggregate, honest read on clinical sign-off so the editor sees one
        // actionable line instead of a flag on every unreviewed item.
        let totalItems = procedures.count + rescueCards.count + kits.count
        let unreviewed = procedures.filter { !$0.reviewer.isClinicallyReviewed }.count
            + rescueCards.filter { !$0.reviewer.isClinicallyReviewed }.count
            + kits.filter { !$0.reviewer.isClinicallyReviewed }.count
        if unreviewed > 0 {
            issues.append(.init(
                severity: .polish,
                procedureID: nil,
                procedureTitle: nil,
                message: "\(unreviewed) of \(totalItems) content items await clinical review; not for unsupervised clinical reliance until reviewed."
            ))
        }

        return issues.sorted { lhs, rhs in
            if lhs.severity.sortOrder != rhs.severity.sortOrder {
                return lhs.severity.sortOrder < rhs.severity.sortOrder
            }
            return lhs.displayMessage.localizedCaseInsensitiveCompare(rhs.displayMessage) == .orderedAscending
        }
    }

    private static func validate(_ procedure: Procedure) -> [ContentValidationIssue] {
        var issues: [ContentValidationIssue] = []

        func add(_ severity: ContentValidationIssue.Severity, _ message: String) {
            issues.append(.init(severity: severity, procedureID: procedure.id, procedureTitle: procedure.title, message: message))
        }

        if procedure.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { add(.blocker, "missing title.") }
        if procedure.lastReviewed.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            add(.blocker, "missing last-reviewed metadata.")
        } else if ContentFreshness.isUnparseableDate(procedure.lastReviewed) {
            add(.blocker, "last-reviewed date '\(procedure.lastReviewed)' is not a valid yyyy-MM-dd date.")
        } else if let days = ContentFreshness.daysSinceReview(procedure.lastReviewed), days > ContentFreshness.stalenessThresholdDays {
            add(.warning, "content is stale: last reviewed \(days) days ago; schedule re-review.")
        }
        if procedure.version.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { add(.blocker, "missing version metadata.") }
        issues.append(contentsOf: provenanceIssues(
            source: procedure.contentSource, reviewer: procedure.reviewer,
            procedureID: procedure.id, title: procedure.title
        ))
        if procedure.tags.isEmpty { add(.warning, "missing search tags/synonyms.") }

        // The equipment checklist persists checked-state on the item string, so
        // duplicate strings collide (toggling one toggles the other).
        let equipmentDuplicates = duplicates(in: procedure.sections.equipment)
        if !equipmentDuplicates.isEmpty {
            add(.warning, "duplicate equipment items collide in the checklist: \(equipmentDuplicates.joined(separator: ", ")).")
        }

        let required: [(String, [String], Int, ContentValidationIssue.Severity)] = [
            ("Shift Mode", procedure.sections.shiftMode, 6, .blocker),
            ("Indications", procedure.sections.indications, 1, .blocker),
            ("Contraindications", procedure.sections.contraindications, 1, .warning),
            ("Anatomy", procedure.sections.anatomy, 1, .warning),
            ("Equipment", procedure.sections.equipment, 5, .blocker),
            ("Positioning", procedure.sections.positioning, 1, .warning),
            ("Steps", procedure.sections.steps, 5, .blocker),
            ("Ultrasound", procedure.sections.ultrasound, 0, .polish),
            ("Confirmation", procedure.sections.confirmation, 1, .warning),
            ("Complications", procedure.sections.complications, 4, .blocker),
            ("Troubleshooting", procedure.sections.troubleshooting, 3, .warning),
            ("Aftercare", procedure.sections.aftercare, 1, .warning),
            ("Documentation", procedure.sections.documentation, 4, .warning),
            ("Senior Pearls", procedure.sections.seniorPearls, 2, .polish),
            ("References", procedure.sections.references, 1, .blocker)
        ]

        for (name, items, minimumCount, severity) in required {
            if items.isEmpty {
                add(severity, "missing \(name) content.")
            } else if items.count < minimumCount {
                add(severity == .blocker ? .warning : severity, "\(name) may be too thin for release-quality content; found \(items.count), target at least \(minimumCount).")
            }
        }

        // Visual assets are an optional enhancement, shown only when a real
        // image is bundled. Validate their structure when present, but do not
        // flag their absence or pending artwork as content issues.
        for asset in procedure.visualAssets ?? [] {
            if asset.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                add(.warning, "visual asset \(asset.id) is missing a title.")
            }
        }

        let allContent = [
            procedure.sections.shiftMode,
            procedure.sections.equipment,
            procedure.sections.steps,
            procedure.sections.complications,
            procedure.sections.troubleshooting,
            procedure.sections.documentation,
            procedure.sections.seniorPearls
        ].flatMap { $0 }

        if allContent.contains(where: { $0.localizedCaseInsensitiveContains("monitor closely") }) {
            add(.polish, "contains vague phrase 'monitor closely'; replace with concrete reassessment actions.")
        }

        // Local-anesthetic safety limits are first-class data for regional
        // anesthesia: a block that states a volume without a weight-based
        // ceiling is a patient-safety defect, not a polish item. Mirrors the
        // Python validator's regional dosing rules.
        if procedure.category == .regionalAnesthesia {
            if let dosing = procedure.dosing {
                if dosing.agents.isEmpty {
                    add(.blocker, "dosing block has no agents; a max-dose section without agents is unusable.")
                }
                for agent in dosing.agents where agent.maxDoseMgPerKg <= 0 {
                    add(.blocker, "dosing agent \(agent.agent) has a nonpositive mg/kg maximum.")
                }
                for agent in dosing.agents where agent.concentrationNote.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    add(.warning, "dosing agent \(agent.agent) is missing a concentration-to-mg conversion note.")
                }
                if dosing.workedExample.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    add(.warning, "dosing block is missing a worked max-dose example.")
                }
                if dosing.cumulativeWarning.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    add(.warning, "dosing block is missing a cumulative-dose warning.")
                }
                if dosing.monitoring.count < 2 {
                    add(.warning, "dosing block needs concrete monitoring/LAST-preparation actions.")
                }
            } else {
                add(.warning, "regional anesthesia procedure is missing structured max-dose (dosing) data.")
            }
        }

        if procedure.difficulty == .advanced || procedure.difficulty == .rareCrash {
            let hasRescueLanguage = procedure.sections.troubleshooting.joined(separator: " ").localizedCaseInsensitiveContains("rescue") ||
                procedure.sections.shiftMode.joined(separator: " ").localizedCaseInsensitiveContains("backup") ||
                procedure.sections.troubleshooting.count >= 4
            if !hasRescueLanguage {
                add(.warning, "high-risk procedure needs an explicit rescue/failure plan.")
            }
        }

        return issues
    }

    private static func validateRescueCoverage(_ procedures: [Procedure], rescueCards: [ComplicationRescueCard]) -> [ContentValidationIssue] {
        let coveredIDs = Set(rescueCards.flatMap(\.relatedProcedureIDs))
        return procedures.compactMap { procedure in
            guard !coveredIDs.contains(procedure.id) else { return nil }
            let isHighRisk = procedure.difficulty == .advanced || procedure.difficulty == .rareCrash
            return ContentValidationIssue(
                severity: isHighRisk ? .warning : .polish,
                procedureID: procedure.id,
                procedureTitle: procedure.title,
                message: isHighRisk
                    ? "high-risk procedure has no rescue card coverage."
                    : "no rescue card coverage."
            )
        }
    }

    private static func validateRescueCards(_ cards: [ComplicationRescueCard], procedureIDs: Set<String>) -> [ContentValidationIssue] {
        var issues: [ContentValidationIssue] = []

        func add(_ severity: ContentValidationIssue.Severity, _ title: String?, _ message: String) {
            issues.append(.init(severity: severity, procedureID: nil, procedureTitle: title, message: message))
        }

        if cards.isEmpty {
            add(.warning, nil, "No rescue cards loaded. Rescue should be a first-class content object, not hardcoded Swift.")
            return issues
        }

        let ids = cards.map(\.id)
        let duplicateIDs = Dictionary(grouping: ids, by: { $0 }).filter { $0.value.count > 1 }.keys.sorted()
        if !duplicateIDs.isEmpty {
            add(.blocker, nil, "Duplicate rescue card IDs: \(duplicateIDs.joined(separator: ", ")).")
        }

        for card in cards {
            if card.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { add(.blocker, card.title, "missing rescue card title.") }
            if card.trigger.isEmpty { add(.blocker, card.title, "missing trigger content.") }
            if card.immediateMoves.count < 3 { add(.blocker, card.title, "needs at least 3 immediate moves.") }
            if card.reassess.count < 2 { add(.warning, card.title, "needs concrete reassessment targets.") }
            if card.avoid.isEmpty { add(.warning, card.title, "missing 'avoid' content.") }
            if card.tags.isEmpty { add(.warning, card.title, "missing search tags.") }
            if card.lastReviewed.isEmpty {
                add(.blocker, card.title, "missing last-reviewed metadata.")
            } else if ContentFreshness.isUnparseableDate(card.lastReviewed) {
                add(.blocker, card.title, "last-reviewed date '\(card.lastReviewed)' is not a valid yyyy-MM-dd date.")
            } else if let days = ContentFreshness.daysSinceReview(card.lastReviewed), days > ContentFreshness.stalenessThresholdDays {
                add(.warning, card.title, "rescue card is stale: last reviewed \(days) days ago; schedule re-review.")
            }
            if card.version.isEmpty { add(.blocker, card.title, "missing version metadata.") }
            if card.references.isEmpty { add(.blocker, card.title, "missing references.") }
            issues.append(contentsOf: provenanceIssues(
                source: card.contentSource, reviewer: card.reviewer,
                procedureID: nil, title: card.title
            ))

            let missingRelations = card.relatedProcedureIDs.filter { !procedureIDs.contains($0) }
            if !missingRelations.isEmpty {
                add(.warning, card.title, "related procedure IDs not found in procedures.json: \(missingRelations.joined(separator: ", ")).")
            }
        }

        return issues
    }

    private static func validateKits(_ kits: [Kit], procedureIDs: Set<String>) -> [ContentValidationIssue] {
        var issues: [ContentValidationIssue] = []

        func add(_ severity: ContentValidationIssue.Severity, _ title: String?, _ message: String) {
            issues.append(.init(severity: severity, procedureID: nil, procedureTitle: title, message: message))
        }

        if kits.isEmpty { return issues }

        let ids = kits.map(\.id)
        let duplicateIDs = Dictionary(grouping: ids, by: { $0 }).filter { $0.value.count > 1 }.keys.sorted()
        if !duplicateIDs.isEmpty {
            add(.blocker, nil, "Duplicate kit IDs: \(duplicateIDs.joined(separator: ", ")).")
        }

        for kit in kits {
            if kit.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { add(.blocker, kit.title, "missing kit title.") }
            if kit.subtitle.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { add(.warning, kit.title, "missing kit subtitle.") }
            if kit.inKit.isEmpty { add(.blocker, kit.title, "inKit content is empty.") }
            if kit.patientSetup.isEmpty { add(.warning, kit.title, "missing patient setup instructions.") }
            if kit.references.isEmpty { add(.blocker, kit.title, "missing references.") }
            if kit.tags.isEmpty { add(.warning, kit.title, "missing search tags.") }

            if kit.lastReviewed.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                add(.blocker, kit.title, "missing last-reviewed metadata.")
            } else if ContentFreshness.isUnparseableDate(kit.lastReviewed) {
                add(.blocker, kit.title, "last-reviewed date '\(kit.lastReviewed)' is not a valid yyyy-MM-dd date.")
            } else if let days = ContentFreshness.daysSinceReview(kit.lastReviewed), days > ContentFreshness.stalenessThresholdDays {
                add(.warning, kit.title, "kit content is stale: last reviewed \(days) days ago; schedule re-review.")
            }
            if kit.version.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { add(.blocker, kit.title, "missing version metadata.") }
            issues.append(contentsOf: provenanceIssues(
                source: kit.contentSource, reviewer: kit.reviewer,
                procedureID: nil, title: kit.title
            ))

            let missingRelations = kit.relatedProcedureIDs.filter { !procedureIDs.contains($0) }
            if !missingRelations.isEmpty {
                add(.warning, kit.title, "related procedure IDs not found in procedures.json: \(missingRelations.joined(separator: ", ")).")
            }

            // Room-setup checked-state is keyed on the item string across
            // inKit + outsideKit combined, so a duplicate toggles in two places.
            let checklistDuplicates = duplicates(in: kit.inKit + kit.outsideKit)
            if !checklistDuplicates.isEmpty {
                add(.warning, kit.title, "duplicate checklist items collide between inKit/outsideKit: \(checklistDuplicates.joined(separator: ", ")).")
            }
        }

        return issues
    }

    /// Provenance rules shared by all content types. Missing provenance is a
    /// warning (the item still reads as an AI draft); a clinically reviewed
    /// status on an item whose words are still an unowned AI draft is a
    /// contradiction and always a blocker. Mirrors the Python validator.
    private static func provenanceIssues(
        source: ContentSource?,
        reviewer: ReviewerStatus,
        procedureID: String?,
        title: String?
    ) -> [ContentValidationIssue] {
        var issues: [ContentValidationIssue] = []
        if source == nil {
            issues.append(.init(
                severity: .warning, procedureID: procedureID, procedureTitle: title,
                message: "missing contentSource provenance; treated as an AI draft."
            ))
        }
        if (source ?? .undeclaredDefault) == .aiDraft && reviewer.isClinicallyReviewed {
            issues.append(.init(
                severity: .blocker, procedureID: procedureID, procedureTitle: title,
                message: "reviewerStatus claims clinical review but contentSource is still 'ai-draft'; a sign-off must update provenance."
            ))
        }
        return issues
    }

    /// Case-sensitive duplicate detection, sorted for stable messages. Matches
    /// the UI's checked-state keying, which compares exact item strings.
    private static func duplicates(in items: [String]) -> [String] {
        Dictionary(grouping: items, by: { $0 })
            .filter { $0.value.count > 1 }
            .keys
            .sorted()
    }
}

private extension ContentValidationIssue.Severity {
    var sortOrder: Int {
        switch self {
        case .blocker: return 0
        case .warning: return 1
        case .polish: return 2
        }
    }
}
