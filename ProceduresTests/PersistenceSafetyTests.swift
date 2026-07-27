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

    func testSavedEquipmentRequiresAnExplicitDecisionInEachAppSession() {
        let firstSession = UserDataStore(defaults: defaults)
        firstSession.toggleEquipment("Ultrasound", for: procedureFixture)

        let nextSession = UserDataStore(defaults: defaults)
        XCTAssertTrue(nextSession.requiresEquipmentSessionDecision(for: procedureFixture))

        nextSession.resumeEquipmentSession(for: procedureFixture)
        XCTAssertFalse(nextSession.requiresEquipmentSessionDecision(for: procedureFixture))
        XCTAssertTrue(nextSession.isEquipmentChecked("Ultrasound", for: procedureFixture))

        let laterSession = UserDataStore(defaults: defaults)
        XCTAssertTrue(laterSession.requiresEquipmentSessionDecision(for: procedureFixture))

        laterSession.resetEquipment(for: procedureFixture)
        let resetSession = UserDataStore(defaults: defaults)
        XCTAssertFalse(resetSession.requiresEquipmentSessionDecision(for: procedureFixture))
        XCTAssertFalse(resetSession.isEquipmentChecked("Ultrasound", for: procedureFixture))
    }

    func testSavedKitRequiresAnExplicitDecisionInEachAppSession() {
        let firstSession = UserDataStore(defaults: defaults)
        firstSession.toggleKitItem("Sterile gown", forKitID: "central-line")

        let nextSession = UserDataStore(defaults: defaults)
        XCTAssertTrue(nextSession.requiresKitSessionDecision(forKitID: "central-line"))

        nextSession.resumeKitSession(withID: "central-line")
        XCTAssertFalse(nextSession.requiresKitSessionDecision(forKitID: "central-line"))
        XCTAssertTrue(nextSession.isKitItemChecked("Sterile gown", forKitID: "central-line"))

        let laterSession = UserDataStore(defaults: defaults)
        XCTAssertTrue(laterSession.requiresKitSessionDecision(forKitID: "central-line"))

        laterSession.resetKit(withID: "central-line")
        let resetSession = UserDataStore(defaults: defaults)
        XCTAssertFalse(resetSession.requiresKitSessionDecision(forKitID: "central-line"))
        XCTAssertFalse(resetSession.isKitItemChecked("Sterile gown", forKitID: "central-line"))
    }

    // MARK: - Review version binding

    func testReviewMarkIsBoundToTheContentVersionItWasRecordedAgainst() {
        let store = UserDataStore(defaults: defaults)
        store.markReviewed(procedureFixture)

        XCTAssertEqual(store.localReviewRecord(for: procedureFixture)?.contentVersion, "1.0")
        XCTAssertEqual(store.reviewVersionState(for: procedureFixture), .current)
        XCTAssertEqual(
            store.supersededReviewCount(procedures: [procedureFixture], rescueCards: [], kits: []),
            0
        )
    }

    func testReviewMarkIsReportedSupersededWhenBundledContentShipsANewVersion() {
        let store = UserDataStore(defaults: defaults)
        store.markReviewed(procedureFixture)

        let updated = procedureFixture(version: "1.1")
        XCTAssertEqual(store.reviewVersionState(for: updated), .superseded(recordedVersion: "1.0"))
        XCTAssertEqual(
            store.supersededReviewCount(procedures: [updated], rescueCards: [], kits: []),
            1,
            "A sign-off must not survive a content update as if it still applied."
        )
    }

    func testLegacyReviewRecordWithoutAVersionReadsAsUnknownBaselineNotApproved() throws {
        try seedReviews(["procedure:central-line": LocalReviewRecord(disposition: .reviewed, date: "2026-07-18")])

        let store = UserDataStore(defaults: defaults)
        XCTAssertEqual(store.reviewVersionState(for: procedureFixture), .unknownBaseline)
        XCTAssertTrue(store.reviewVersionState(for: procedureFixture)?.needsRecheck == true)
        XCTAssertEqual(
            store.supersededReviewCount(procedures: [procedureFixture], rescueCards: [], kits: []),
            1,
            "A record saved before version tracking cannot be claimed as current approval."
        )
    }

    func testNonReviewedDispositionsAreNotCountedAsSupersededWork() {
        let store = UserDataStore(defaults: defaults)
        store.setReviewDisposition(.needsEdits, for: procedureFixture)

        let updated = procedureFixture(version: "2.0")
        XCTAssertEqual(
            store.supersededReviewCount(procedures: [updated], rescueCards: [], kits: []),
            0,
            "Needs Edits is already queued work; it must not double-count as a stale sign-off."
        )
    }

    private var record: LocalReviewRecord {
        LocalReviewRecord(disposition: .reviewed, date: "2026-07-18")
    }

    private var procedureFixture: Procedure { procedureFixture(version: "1.0") }

    private func procedureFixture(version: String) -> Procedure {
        let json = """
        {
          "id": "central-line",
          "title": "Central Venous Catheter",
          "category": "Vascular Access",
          "difficulty": "Advanced",
          "reviewTime": "3 min",
          "setting": ["ED"],
          "lastReviewed": "2026-07-18",
          "version": "\(version)",
          "tags": [],
          "visualAssets": null,
          "reviewerStatus": null,
          "sections": {
            "shiftMode": [],
            "indications": [],
            "contraindications": [],
            "anatomy": [],
            "equipment": ["Ultrasound"],
            "positioning": [],
            "steps": [],
            "ultrasound": [],
            "confirmation": [],
            "troubleshooting": [],
            "complications": [],
            "aftercare": [],
            "documentation": [],
            "seniorPearls": [],
            "references": []
          }
        }
        """
        return try! JSONDecoder().decode(Procedure.self, from: Data(json.utf8))
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
