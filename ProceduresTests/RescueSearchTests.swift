import XCTest
@testable import Procedures

/// Regression coverage for the rescue-card search bug where synonym expansion
/// used AND-semantics and made clinical shorthand return zero results. These
/// lock in the AND-across-typed-words, OR-within-synonyms behavior.
@MainActor
final class RescueSearchTests: XCTestCase {
    func testShorthandReturnsRescueCards() {
        let repo = ProcedureRepository()
        XCTAssertFalse(repo.searchRescueCards("ett").isEmpty, "ETT shorthand must return rescue cards")
        XCTAssertFalse(repo.searchRescueCards("tube").isEmpty, "tube shorthand must return rescue cards")
        XCTAssertFalse(repo.searchRescueCards("rsi").isEmpty, "RSI shorthand must return rescue cards")
    }

    func testMultiWordQueryStillNarrows() {
        let repo = ProcedureRepository()
        let results = repo.searchRescueCards("lost wire")
        XCTAssertTrue(results.contains { $0.id == "lost_wire" }, "expected the lost-wire card for a precise two-word query")
    }

    func testNonsenseQueryReturnsNothing() {
        let repo = ProcedureRepository()
        XCTAssertTrue(repo.searchRescueCards("zzzznotaclinicalterm").isEmpty)
    }

    func testEmptyQueryReturnsEveryCard() {
        let repo = ProcedureRepository()
        XCTAssertEqual(repo.searchRescueCards("   ").count, repo.rescueCards.count)
    }

    func testSynonymGroupingIsOrNotAnd() {
        // The original bug demanded every synonym be present. A token must now
        // be satisfied by itself OR any single synonym.
        let group = ClinicalSynonyms.group(for: "ett")
        XCTAssertTrue(group.contains("ett"))
        XCTAssertTrue(group.contains("intubation"))
        XCTAssertGreaterThan(group.count, 1)
    }

    func testProcedureSearchUnderstandsShorthand() {
        let repo = ProcedureRepository()
        XCTAssertTrue(repo.search("cric").contains { $0.id == "cricothyrotomy" })
        XCTAssertTrue(repo.search("lp").contains { $0.id == "lumbar_puncture" })
        XCTAssertTrue(repo.search("pacer").contains { $0.id == "transvenous_pacemaker" })
    }

    func testProcedureAndRescueShareOneSynonymSource() {
        // Both surfaces read ClinicalSynonyms, so a key defined once is visible
        // to each. Guard against the two maps drifting apart again.
        XCTAssertNotNil(ClinicalSynonyms.expansions["ett"])
        XCTAssertNotNil(ClinicalSynonyms.expansions["hypotension"])
    }
}
