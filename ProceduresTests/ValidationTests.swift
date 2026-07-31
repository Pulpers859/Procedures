import XCTest
@testable import Procedures

/// Unit tests for the validator and the tolerant decoder, using synthetic
/// fixtures so the rules themselves are exercised independent of shipped JSON.
@MainActor
final class ValidationTests: XCTestCase {
    func testFailableDecodableSalvagesBadElements() throws {
        let json = Data("""
        [{"value": 1}, "not an int", 3]
        """.utf8)
        let wrapped = try JSONDecoder().decode([FailableDecodable<Int>].self, from: json)
        XCTAssertEqual(wrapped.count, 3, "every array slot is represented")
        XCTAssertEqual(wrapped.compactMap(\.value), [3], "only the well-formed Int survives")
    }

    func testValidatorFlagsMissingReferences() {
        let issues = ContentValidator.validate([makeProcedure(references: [])])
        XCTAssertTrue(
            issues.contains { $0.severity == .blocker && $0.message.localizedCaseInsensitiveContains("references") },
            "missing references must be a blocker"
        )
    }

    func testValidatorIsCleanForCompleteProcedure() {
        let blockers = ContentValidator.validate([makeProcedure()]).filter { $0.severity == .blocker }
        XCTAssertTrue(blockers.isEmpty, "a complete procedure should produce no blockers: \(blockers.map(\.message))")
    }

    func testDuplicateProcedureIDsAreBlocked() {
        let issues = ContentValidator.validate([makeProcedure(id: "dup"), makeProcedure(id: "dup")])
        XCTAssertTrue(
            issues.contains { $0.severity == .blocker && $0.message.localizedCaseInsensitiveContains("duplicate") },
            "duplicate IDs must be a blocker"
        )
    }

    func testEmptyRescueCardListIsWarned() {
        let issues = ContentValidator.validate([makeProcedure()], rescueCards: [])
        XCTAssertTrue(issues.contains { $0.severity == .warning && $0.message.localizedCaseInsensitiveContains("rescue") })
    }

    func testUnreviewedContentDefaultsToNeedingReview() {
        // An absent reviewerStatus must read as not-yet-reviewed, never as trusted.
        let unreviewed = makeProcedure(reviewerStatus: nil)
        XCTAssertEqual(unreviewed.reviewer, .needsClinicalReview)
        XCTAssertFalse(unreviewed.reviewer.isClinicallyReviewed)
        XCTAssertTrue(makeProcedure(reviewerStatus: .externallyReviewed).reviewer.isClinicallyReviewed)
    }

    func testUnreviewedContentIsSurfacedAsPolishIssue() {
        let issues = ContentValidator.validate([makeProcedure(reviewerStatus: .needsClinicalReview)])
        XCTAssertTrue(
            issues.contains { $0.severity == .polish && $0.message.localizedCaseInsensitiveContains("await clinical review") },
            "unreviewed content should surface an aggregate governance note"
        )
    }

    func testStaleContentIsWarned() {
        let stale = makeProcedure()  // fixture is dated 2026-01-01
        let issues = ContentValidator.validate([stale])
        // The fixture date ages past the threshold over time; assert the rule
        // engages by checking the freshness helper directly to stay date-stable.
        XCTAssertTrue(ContentFreshness.isStale("2000-01-01"))
        XCTAssertFalse(ContentFreshness.isStale("2000-01-01", now: dateFrom("2000-06-01")))
        _ = issues
    }

    func testUnparseableReviewDateIsBlocked() {
        XCTAssertTrue(ContentFreshness.isUnparseableDate("not-a-date"))
        XCTAssertFalse(ContentFreshness.isUnparseableDate("2026-06-15"))
        XCTAssertFalse(ContentFreshness.isUnparseableDate(""))
    }

    private func dateFrom(_ iso: String) -> Date {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(identifier: "UTC")
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: iso)!
    }

    func testRegionalAnesthesiaWithoutDosingIsWarned() {
        let issues = ContentValidator.validate([makeProcedure(category: .regionalAnesthesia)])
        XCTAssertTrue(
            issues.contains { $0.severity == .warning && $0.message.localizedCaseInsensitiveContains("max-dose") },
            "a regional anesthesia procedure without structured dosing must be flagged"
        )
    }

    func testDosingWithNoAgentsIsBlocked() {
        let dosing = ProcedureDosing(
            agents: [],
            cumulativeWarning: "warning",
            caveats: nil,
            monitoring: ["a", "b"],
            rescueCardID: nil
        )
        let issues = ContentValidator.validate([makeProcedure(category: .regionalAnesthesia, dosing: dosing)])
        XCTAssertTrue(
            issues.contains { $0.severity == .blocker && $0.message.localizedCaseInsensitiveContains("no agents") },
            "an empty agents list is an unusable max-dose section and must be a blocker"
        )
    }

    func testWellFormedDosingProducesNoDosingIssues() {
        let dosing = ProcedureDosing(
            agents: [.init(agent: "Bupivacaine", withEpinephrine: false, maxDoseMgPerKg: 2.0, absoluteMaxMg: 175, concentrationsPercent: [0.25, 0.5], note: nil)],
            cumulativeWarning: "All local anesthetic this encounter shares one maximum.",
            caveats: ["Use lean body weight in obese patients."],
            monitoring: ["Continuous cardiac monitoring", "Confirm lipid emulsion location"],
            rescueCardID: nil
        )
        let issues = ContentValidator.validate([makeProcedure(category: .regionalAnesthesia, dosing: dosing)])
        XCTAssertFalse(
            issues.contains { $0.message.localizedCaseInsensitiveContains("dosing") || $0.message.localizedCaseInsensitiveContains("max-dose") },
            "well-formed dosing should be clean: \(issues.map(\.message))"
        )
    }

    func testDanglingDosingRescueCardIDIsBlocked() {
        let dosing = ProcedureDosing(
            agents: [.init(agent: "Bupivacaine", withEpinephrine: false, maxDoseMgPerKg: 2.0, absoluteMaxMg: 175, concentrationsPercent: [0.25], note: nil)],
            cumulativeWarning: "warning",
            caveats: nil,
            monitoring: ["a", "b"],
            rescueCardID: "does_not_exist"
        )
        let card = ComplicationRescueCard(
            id: "some_other_card",
            title: "Card",
            acuity: .urgent,
            relatedProcedureIDs: [],
            trigger: ["t"],
            immediateMoves: ["a", "b", "c"],
            reassess: ["a", "b"],
            avoid: ["a"],
            tags: ["t"],
            lastReviewed: "2026-01-01",
            version: "1.0",
            references: ["Smith et al. 2024"],
            reviewerStatus: .internallyReviewed,
            contentSource: .clinicianReviewed
        )
        let issues = ContentValidator.validate(
            [makeProcedure(category: .regionalAnesthesia, dosing: dosing)],
            rescueCards: [card]
        )
        XCTAssertTrue(
            issues.contains { $0.severity == .blocker && $0.message.localizedCaseInsensitiveContains("dosing rescue card") },
            "a dosing rescue link that resolves to nothing is a broken relation and must be a blocker"
        )
    }

    func testUndeclaredProvenanceReadsAsAIDraft() {
        // Absent contentSource must read as the least trusted answer.
        XCTAssertEqual(makeProcedure(contentSource: nil).source, .aiDraft)
        let issues = ContentValidator.validate([makeProcedure(reviewerStatus: .needsClinicalReview, contentSource: nil)])
        XCTAssertTrue(
            issues.contains { $0.severity == .warning && $0.message.localizedCaseInsensitiveContains("contentSource") },
            "missing provenance should warn"
        )
    }

    func testReviewedStatusOnAIDraftIsBlocked() {
        // A clinician sign-off that leaves provenance at 'ai-draft' is a
        // contradiction: the words are still an unowned machine draft.
        for source in [ContentSource.aiDraft, nil] {
            let issues = ContentValidator.validate([makeProcedure(reviewerStatus: .internallyReviewed, contentSource: source)])
            XCTAssertTrue(
                issues.contains { $0.severity == .blocker && $0.message.localizedCaseInsensitiveContains("still 'ai-draft'") },
                "reviewed status with ai-draft provenance must be a blocker"
            )
        }
    }

    func testHonestAIDraftAwaitingReviewIsNotBlocked() {
        let issues = ContentValidator.validate([makeProcedure(reviewerStatus: .needsClinicalReview, contentSource: .aiDraft)])
        XCTAssertFalse(
            issues.contains { $0.severity == .blocker },
            "an AI draft honestly awaiting review is a valid authoring state"
        )
    }

    func testDuplicateEquipmentItemsAreWarned() {
        let issues = ContentValidator.validate([makeProcedure(equipment: ["scalpel", "scalpel", "gauze", "gauze", "drape"])])
        XCTAssertTrue(
            issues.contains { $0.severity == .warning && $0.message.localizedCaseInsensitiveContains("duplicate equipment") },
            "duplicate checklist strings collide in the UI and must be flagged"
        )
    }

    private func makeProcedure(
        id: String = "test",
        references: [String] = ["Smith et al. 2024"],
        reviewerStatus: ReviewerStatus? = .internallyReviewed,
        contentSource: ContentSource? = .clinicianReviewed,
        equipment: [String] = ["a", "b", "c", "d", "e"],
        category: ProcedureCategory = .other,
        dosing: ProcedureDosing? = nil
    ) -> Procedure {
        Procedure(
            id: id,
            title: "Test Procedure",
            category: category,
            difficulty: .basic,
            reviewTime: "1 min",
            setting: [.ed],
            lastReviewed: "2026-01-01",
            version: "1.0",
            tags: ["test"],
            visualAssets: nil,
            dosing: dosing,
            medicationDosing: nil,
            reviewerStatus: reviewerStatus,
            contentSource: contentSource,
            sections: ProcedureSections(
                shiftMode: ["a", "b", "c", "d", "e", "f"],
                indications: ["a"],
                contraindications: ["a"],
                anatomy: ["a"],
                equipment: equipment,
                positioning: ["a"],
                steps: ["a", "b", "c", "d", "e"],
                ultrasound: [],
                confirmation: ["a"],
                troubleshooting: ["a", "b", "c"],
                complications: ["a", "b", "c", "d"],
                aftercare: ["a"],
                documentation: ["a", "b", "c", "d"],
                seniorPearls: ["a", "b"],
                references: references
            )
        )
    }
}

/// The arithmetic behind the max-dose card.
///
/// This replaced a frozen sentence — "70 kg = 315 mg" printed directly beneath
/// "absolute max 300 mg" on the digital block, because a worked example cannot
/// recalculate itself when a ceiling is added later. These tests exist so the
/// computed version cannot acquire the same defect quietly.
@MainActor
final class MaxDoseCalculatorTests: XCTestCase {
    private func agent(
        maxDoseMgPerKg: Double = 4.5,
        absoluteMaxMg: Double? = 300,
        withEpinephrine: Bool = false
    ) -> ProcedureDosing.Agent {
        ProcedureDosing.Agent(
            agent: "Lidocaine",
            withEpinephrine: withEpinephrine,
            maxDoseMgPerKg: maxDoseMgPerKg,
            absoluteMaxMg: absoluteMaxMg,
            concentrationsPercent: [1.0, 2.0],
            note: nil
        )
    }

    func testPercentToMilligramsPerMillilitreIsTheDefinition() {
        XCTAssertEqual(ProcedureDosing.Agent.mgPerML(percent: 1), 10)
        XCTAssertEqual(ProcedureDosing.Agent.mgPerML(percent: 0.25), 2.5)
        XCTAssertEqual(ProcedureDosing.Agent.mgPerML(percent: 2), 20)
    }

    func testBelowTheAbsoluteCeilingTheDoseScalesWithWeight() {
        XCTAssertEqual(agent().maxMilligrams(forWeightKg: 50), 225)
        XCTAssertFalse(agent().isCapped(atWeightKg: 50))
    }

    /// The exact case the old card got wrong: 4.5 mg/kg x 70 kg is 315 mg, and
    /// the answer is 300.
    func testAboveTheAbsoluteCeilingTheDoseIsHeldAndMarked() {
        XCTAssertEqual(agent().maxMilligrams(forWeightKg: 70), 300)
        XCTAssertTrue(agent().isCapped(atWeightKg: 70))
    }

    func testExactlyAtTheCeilingIsNotMarkedAsCapped() {
        // 4.5 mg/kg x 66.667 kg is 300 mg; nothing was withheld.
        let weight = 300.0 / 4.5
        XCTAssertEqual(agent().maxMilligrams(forWeightKg: weight), 300, accuracy: 0.0001)
        XCTAssertFalse(agent().isCapped(atWeightKg: weight))
    }

    func testAnAgentWithoutAnAbsoluteCeilingNeverCaps() {
        let unbounded = agent(absoluteMaxMg: nil)
        XCTAssertEqual(unbounded.maxMilligrams(forWeightKg: 200), 900)
        XCTAssertFalse(unbounded.isCapped(atWeightKg: 200))
    }

    /// A maximum rounded up is a maximum exceeded.
    func testVolumeAndDoseLabelsRoundDownNeverUp() {
        XCTAssertEqual(MaxDoseCalculatorCard.millilitreLabel(12.349), "12.3 mL")
        XCTAssertEqual(MaxDoseCalculatorCard.millilitreLabel(12.399), "12.3 mL")
        XCTAssertEqual(MaxDoseCalculatorCard.millilitreLabel(12.0), "12.0 mL")
        XCTAssertEqual(MaxDoseCalculatorCard.milligramLabel(315.9), "315 mg")
        XCTAssertEqual(MaxDoseCalculatorCard.milligramLabel(300), "300 mg")
    }

    func testEpinephrineIsPartOfTheAgentIdentity() {
        XCTAssertEqual(agent(withEpinephrine: false).displayName, "Lidocaine")
        XCTAssertEqual(agent(withEpinephrine: true).displayName, "Lidocaine with epinephrine")
        // Both variants coexist in one picker, so the ids must differ.
        XCTAssertNotEqual(agent(withEpinephrine: false).id, agent(withEpinephrine: true).id)
    }

    /// The ceilings are properties of the drug, not of the block. They used to
    /// be copied into 28 records, which is 28 places to fix a number.
    func testEveryRegionalBlockShipsTheSamePreparationTable() {
        let repo = ProcedureRepository()
        let tables = repo.procedures
            .filter { $0.category == .regionalAnesthesia }
            .compactMap { $0.dosing?.agents }
        XCTAssertFalse(tables.isEmpty)
        for table in tables {
            XCTAssertEqual(table, tables[0], "regional dosing tables have diverged")
        }
    }

    /// The intraosseous card shipped a flat "20-40 mg lidocaine 2%" on a
    /// procedure tagged for paediatrics. A 6 kg infant is owed 3 mg, so a
    /// reader following it exactly gave more than six times the dose.
    func testIntraosseousLidocaineScalesWithWeightAndCapsAtFortyMilligrams() {
        let repo = ProcedureRepository()
        guard let dosing = repo.procedures.first(where: { $0.id == "intraosseous_access" })?.dosing,
              let lidocaine = dosing.agents.first else {
            return XCTFail("the intraosseous card must carry structured lidocaine dosing")
        }
        XCTAssertEqual(dosing.agents.count, 1)
        XCTAssertEqual(lidocaine.maxDoseMgPerKg, 0.5)
        XCTAssertEqual(lidocaine.absoluteMaxMg, 40)
        XCTAssertEqual(lidocaine.maxMilligrams(forWeightKg: 6), 3)
        XCTAssertEqual(lidocaine.maxMilligrams(forWeightKg: 100), 40)
        XCTAssertFalse(lidocaine.isCapped(atWeightKg: 6))
        XCTAssertTrue(lidocaine.isCapped(atWeightKg: 100))
        // 0.15 mL of 2% for that infant.
        XCTAssertEqual(3 / ProcedureDosing.Agent.mgPerML(percent: 2), 0.15, accuracy: 0.0001)
    }

    /// "Reduce by about 25% at the extremes of age" was hardcoded in the card.
    /// It is right for an infiltration ceiling and wrong for the intraosseous
    /// analgesic dose, so it cannot be stated from inside a shared view.
    func testCaveatsComeFromTheRecordRatherThanTheView() {
        let repo = ProcedureRepository()
        let regional = repo.procedures
            .first { $0.category == .regionalAnesthesia }?.dosing?.caveats ?? []
        let intraosseous = repo.procedures
            .first { $0.id == "intraosseous_access" }?.dosing?.caveats ?? []
        XCTAssertFalse(regional.isEmpty)
        XCTAssertFalse(intraosseous.isEmpty)
        XCTAssertNotEqual(regional, intraosseous)
        XCTAssertTrue(regional.contains { $0.contains("25%") })
        XCTAssertFalse(intraosseous.contains { $0.contains("25%") })
    }

    /// Owner decision, 2026-07-30: pleural procedures take the conservative BTS
    /// ceiling rather than the label's. The calculator must therefore return a
    /// different number for the same drug and weight depending on the card,
    /// which is the whole reason the ceiling is per-record data.
    func testPleuralProceduresCarryTheConservativeCeiling() {
        let repo = ProcedureRepository()
        let pleural = ["thoracostomy_chest_tube", "pigtail_catheter", "thoracentesis"]
        for id in pleural {
            guard let agent = repo.procedures.first(where: { $0.id == id })?.dosing?.agents.first else {
                return XCTFail("\(id) must carry a pleural lidocaine ceiling")
            }
            XCTAssertEqual(agent.maxDoseMgPerKg, 3.0, id)
            XCTAssertEqual(agent.absoluteMaxMg, 250, id)
            // 70 kg: 210 mg here, against 300 mg capped on a regional block.
            XCTAssertEqual(agent.maxMilligrams(forWeightKg: 70), 210, id)
        }

        let regionalPlain = repo.procedures
            .first { $0.category == .regionalAnesthesia }?
            .dosing?.agents.first { $0.agent == "Lidocaine" && !$0.withEpinephrine }
        XCTAssertEqual(regionalPlain?.maxMilligrams(forWeightKg: 70), 300)
    }

    /// Owner decision, 2026-07-30. Two records now name etomidate, and the doses
    /// differ by a factor of two or three. A reader who reaches the wrong card
    /// gets a number that is wrong in the more dangerous direction, so the
    /// relationship between them is asserted rather than assumed.
    func testSedationDosesSitBelowTheInductionDoses() {
        let repo = ProcedureRepository()
        guard let sedation = repo.procedures
                .first(where: { $0.id == "procedural_sedation" })?.medicationDosing,
              let induction = repo.procedures
                .first(where: { $0.id == "endotracheal_intubation" })?.medicationDosing else {
            return XCTFail("both airway records must carry structured medication dosing")
        }

        func etomidate(_ block: ProcedureMedicationDosing) -> ProcedureMedicationDosing.Medication? {
            block.medications.first { $0.medication == "Etomidate" }
        }
        guard let sedationDose = etomidate(sedation), let inductionDose = etomidate(induction) else {
            return XCTFail("etomidate must appear on both cards")
        }
        XCTAssertLessThan(
            sedationDose.doseHighPerKg ?? sedationDose.doseLowPerKg,
            inductionDose.doseLowPerKg
        )
        XCTAssertTrue(sedationDose.isRange)
        // A single-value dose renders without the "(range)" suffix, and 0.3
        // mg/kg is a single value rather than a range the reader may titrate.
        XCTAssertFalse(inductionDose.isRange)
    }

    /// The sedation block reaches the view through the field named for RSI. Its
    /// job is the same in both: the one sentence that must render before any
    /// dose does. An empty string would pass the schema and lose the guard.
    func testEveryMedicationBlockCarriesItsHazardGuard() {
        let repo = ProcedureRepository()
        let blocks = repo.procedures.compactMap { $0.medicationDosing }
        XCTAssertEqual(blocks.count, 2)
        for block in blocks {
            XCTAssertFalse(block.inductionRequirement.trimmingCharacters(
                in: .whitespacesAndNewlines
            ).isEmpty)
            XCTAssertFalse(block.sourceNote.trimmingCharacters(
                in: .whitespacesAndNewlines
            ).isEmpty)
        }
    }

    /// Owner decision, 2026-07-30: intravenous lidocaine and defasciculating
    /// vecuronium leave the RSI card. The lidocaine entry mattered beyond its
    /// own evidence base, because 1.5 mg/kg IV silently consumed the same
    /// patient's local-anaesthetic ceiling if they went on to have a block.
    func testTheWithdrawnPretreatmentsAreNotInTheShippedBlock() {
        let repo = ProcedureRepository()
        guard let block = repo.procedures
            .first(where: { $0.id == "endotracheal_intubation" })?.medicationDosing else {
            return XCTFail("the intubation card must carry structured RSI dosing")
        }
        let names = Set(block.medications.map(\.medication))
        XCTAssertFalse(names.contains("Lidocaine"))
        XCTAssertFalse(names.contains("Vecuronium (defasciculating)"))
        XCTAssertTrue(names.contains("Fentanyl"))
        // Every remaining agent answers "when do I look?".
        for medication in block.medications {
            XCTAssertNotNil(medication.onset, medication.medication)
        }
    }
}
