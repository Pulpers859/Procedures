import XCTest
@testable import Procedures

@MainActor
final class PersistenceSafetyTests: XCTestCase {
    private var defaults: UserDefaults!
    private var suiteName: String!

    override func setUp() {
        super.setUp()
        suiteName = "PersistenceSafetyTests.\(UUID().uuidString)"
        defaults = UserDefaults(suiteName: suiteName)
        defaults.removePersistentDomain(forName: suiteName)
    }

    override func tearDown() {
        defaults.removePersistentDomain(forName: suiteName)
        defaults = nil
        suiteName = nil
        super.tearDown()
    }

    func testFailedRescueLoadPreservesRescueReviewsWhileCompleteDomainsPrune() throws {
        try seedReviews([
            "procedure:kept": record,
            "procedure:removed": record,
            "rescue:preserved": record,
            "kit:kept": record,
        ])

        let store = UserDataStore(defaults: defaults)
        store.reconcileLoadedContent(
            validProcedureIDs: ["kept"],
            validRescueCardIDs: nil,
            validKitIDs: ["kept"]
        )

        let reloaded = UserDataStore(defaults: defaults)
        XCTAssertNotNil(reloaded.locallyReviewedContent["rescue:preserved"])
        XCTAssertNil(reloaded.locallyReviewedContent["procedure:removed"])
        XCTAssertNotNil(reloaded.locallyReviewedContent["procedure:kept"])
        XCTAssertNotNil(reloaded.locallyReviewedContent["kit:kept"])
    }

    func testPartialProcedureLoadPreservesProcedureScopedData() throws {
        defaults.set(["preserved"], forKey: "Procedures.favoriteIDs")
        try seedStringSets(
            ["preserved": ["Ultrasound"]],
            key: "Procedures.checkedEquipment"
        )
        try seedReviews(["procedure:preserved": record])

        let store = UserDataStore(defaults: defaults)
        store.reconcileLoadedContent(
            validProcedureIDs: nil,
            validRescueCardIDs: ["rescue"],
            validKitIDs: ["kit"]
        )

        let reloaded = UserDataStore(defaults: defaults)
        XCTAssertTrue(reloaded.favoriteIDs.contains("preserved"))
        XCTAssertEqual(reloaded.checkedEquipment["preserved"], Set(["Ultrasound"]))
        XCTAssertNotNil(reloaded.locallyReviewedContent["procedure:preserved"])
    }

    func testPartialKitLoadPreservesKitChecklistAndReview() throws {
        try seedStringSets(
            ["preserved": ["Sterile gown"]],
            key: "Procedures.kitCheckedItems"
        )
        try seedReviews(["kit:preserved": record])

        let store = UserDataStore(defaults: defaults)
        store.reconcileLoadedContent(
            validProcedureIDs: ["procedure"],
            validRescueCardIDs: ["rescue"],
            validKitIDs: nil
        )

        let reloaded = UserDataStore(defaults: defaults)
        XCTAssertEqual(reloaded.kitCheckedItems["preserved"], Set(["Sterile gown"]))
        XCTAssertNotNil(reloaded.locallyReviewedContent["kit:preserved"])
    }

    func testCompleteLoadStillPrunesRemovedData() throws {
        defaults.set(["kept", "removed"], forKey: "Procedures.favoriteIDs")
        try seedStringSets(
            ["kept": ["A"], "removed": ["B"]],
            key: "Procedures.checkedEquipment"
        )
        try seedStringSets(
            ["kept": ["A"], "removed": ["B"]],
            key: "Procedures.kitCheckedItems"
        )
        try seedReviews([
            "procedure:kept": record,
            "procedure:removed": record,
            "rescue:kept": record,
            "rescue:removed": record,
            "kit:kept": record,
            "kit:removed": record,
        ])

        let store = UserDataStore(defaults: defaults)
        store.reconcileLoadedContent(
            validProcedureIDs: ["kept"],
            validRescueCardIDs: ["kept"],
            validKitIDs: ["kept"]
        )

        let reloaded = UserDataStore(defaults: defaults)
        XCTAssertEqual(reloaded.favoriteIDs, Set(["kept"]))
        XCTAssertEqual(Set(reloaded.checkedEquipment.keys), Set(["kept"]))
        XCTAssertEqual(Set(reloaded.kitCheckedItems.keys), Set(["kept"]))
        XCTAssertEqual(
            Set(reloaded.locallyReviewedContent.keys),
            Set(["procedure:kept", "rescue:kept", "kit:kept"])
        )
    }

    func testLoadWarningMakesIDsNonAuthoritative() {
        let ids: Set<String> = ["decoded"]

        XCTAssertEqual(
            ContentLoadAuthority.authoritativeIDs(ids, loadError: nil, loadWarning: nil),
            ids
        )
        XCTAssertNil(ContentLoadAuthority.authoritativeIDs(ids, loadError: "failed", loadWarning: nil))
        XCTAssertNil(ContentLoadAuthority.authoritativeIDs(ids, loadError: nil, loadWarning: "one dropped"))
        XCTAssertNil(ContentLoadAuthority.authoritativeIDs([], loadError: nil, loadWarning: nil))
    }

    private var record: LocalReviewRecord {
        LocalReviewRecord(disposition: .reviewed, date: "2026-07-18")
    }

    private func seedReviews(_ reviews: [String: LocalReviewRecord]) throws {
        defaults.set(
            try JSONEncoder().encode(reviews),
            forKey: "Procedures.locallyReviewedContent"
        )
    }

    private func seedStringSets(_ values: [String: [String]], key: String) throws {
        defaults.set(try JSONEncoder().encode(values), forKey: key)
    }
}
