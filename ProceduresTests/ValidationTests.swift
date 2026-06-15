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

    private func makeProcedure(id: String = "test", references: [String] = ["Smith et al. 2024"]) -> Procedure {
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
