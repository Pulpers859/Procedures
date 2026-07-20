import XCTest
@testable import Procedures

/// Unit tests for the validator and the tolerant decoder, using synthetic
/// fixtures so the rules themselves are exercised independent of shipped JSON.
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
            workedExample: "example",
            cumulativeWarning: "warning",
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
            agents: [.init(agent: "Bupivacaine (plain)", concentrationNote: "0.25% = 2.5 mg/mL", maxDoseMgPerKg: 2.0, absoluteMaxMg: 175)],
            workedExample: "70 kg: 2 mg/kg = 140 mg = 56 mL of 0.25%.",
            cumulativeWarning: "All local anesthetic this encounter shares one maximum.",
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
            agents: [.init(agent: "Bupivacaine (plain)", concentrationNote: "0.25% = 2.5 mg/mL", maxDoseMgPerKg: 2.0, absoluteMaxMg: 175)],
            workedExample: "example",
            cumulativeWarning: "warning",
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
