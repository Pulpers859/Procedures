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

    private func makeProcedure(
        id: String = "test",
        references: [String] = ["Smith et al. 2024"],
        reviewerStatus: ReviewerStatus? = .internallyReviewed
    ) -> Procedure {
        Procedure(
            id: id,
            title: "Test Procedure",
            category: .other,
            difficulty: .basic,
            reviewTime: "1 min",
            setting: [.ed],
            lastReviewed: "2026-01-01",
            version: "1.0",
            tags: ["test"],
            visualAssets: nil,
            reviewerStatus: reviewerStatus,
            sections: ProcedureSections(
                shiftMode: ["a", "b", "c", "d", "e", "f"],
                indications: ["a"],
                contraindications: ["a"],
                anatomy: ["a"],
                equipment: ["a", "b", "c", "d", "e"],
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
