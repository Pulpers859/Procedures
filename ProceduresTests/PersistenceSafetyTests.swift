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

    /// The session gate was only ever reset by constructing the store — a cold
    /// launch. iOS keeps an app resident for days, so ticking off eight items
    /// mid-case, backgrounding, and reopening the same procedure two days later
    /// skipped the "may be from a prior patient or room" confirmation entirely
    /// and rendered the old ticks as the current room's state.
    func testLeavingTheAppEndsAnInProgressChecklistSession() {
        let store = UserDataStore(defaults: defaults)
        store.toggleEquipment("Ultrasound", for: procedureFixture)
        store.toggleKitItem("Sterile gown", forKitID: "central-line")

        // Mid-case, the session is live and must not nag.
        XCTAssertFalse(store.requiresEquipmentSessionDecision(for: procedureFixture))
        XCTAssertFalse(store.requiresKitSessionDecision(forKitID: "central-line"))

        store.endActiveChecklistSessions()

        XCTAssertTrue(store.requiresEquipmentSessionDecision(for: procedureFixture))
        XCTAssertTrue(store.requiresKitSessionDecision(forKitID: "central-line"))
        // The ticks themselves survive — the reader is asked, not overruled.
        XCTAssertTrue(store.isEquipmentChecked("Ultrasound", for: procedureFixture))
        XCTAssertTrue(store.isKitItemChecked("Sterile gown", forKitID: "central-line"))
    }

    func testEndingSessionsWithNothingCheckedAsksNothing() {
        let store = UserDataStore(defaults: defaults)
        store.endActiveChecklistSessions()
        XCTAssertFalse(store.requiresEquipmentSessionDecision(for: procedureFixture))
    }

    // MARK: - Review content state

    func testReviewCapturesTheMaterialFingerprintItWasRecordedAgainst() {
        let store = UserDataStore(defaults: defaults)
        store.markReviewed(procedureFixture)

        XCTAssertEqual(store.localReviewRecord(for: procedureFixture)?.contentVersion, "1.0")
        XCTAssertNotNil(store.localReviewRecord(for: procedureFixture)?.materialFingerprint)
        XCTAssertEqual(store.reviewContentState(for: procedureFixture), .unchanged)
    }

    func testEditorialChangesNeverDisturbAReview() {
        // A version bump, new tags, or reworded references must not cost a
        // clinician their sign-off. Only material clinical text counts.
        let store = UserDataStore(defaults: defaults)
        store.markReviewed(procedureFixture)

        let editorialOnly = procedureFixture(version: "9.9", tags: ["new", "tags"])
        XCTAssertEqual(
            store.reviewContentState(for: editorialOnly), .unchanged,
            "A version bump alone must not flag a review."
        )
        XCTAssertEqual(
            store.changedSinceReviewCount(procedures: [editorialOnly], rescueCards: [], kits: []),
            0
        )
    }

    func testChangedStepsFlagTheReviewWithoutRevokingIt() {
        let store = UserDataStore(defaults: defaults)
        store.markReviewed(procedureFixture)

        let rewritten = procedureFixture(version: "1.0", steps: ["Completely different step"])
        XCTAssertEqual(store.reviewContentState(for: rewritten), .materialChanged)
        XCTAssertEqual(
            store.changedSinceReviewCount(procedures: [rewritten], rescueCards: [], kits: []),
            1
        )
        // The review itself survives: still Reviewed, still counted as done.
        XCTAssertEqual(store.localReviewRecord(for: rewritten)?.disposition, .reviewed)
        XCTAssertEqual(
            store.localReviewCount(procedures: [rewritten], rescueCards: [], kits: []),
            1,
            "A content change must never move completed review work backwards."
        )
    }

    func testLegacyReviewWithoutAFingerprintIsSilentNotFlagged() {
        try? seedReviews(["procedure:central-line": LocalReviewRecord(disposition: .reviewed, date: "2026-07-18")])

        let store = UserDataStore(defaults: defaults)
        XCTAssertEqual(store.reviewContentState(for: procedureFixture), .unknownBaseline)
        XCTAssertEqual(
            store.changedSinceReviewCount(procedures: [procedureFixture], rescueCards: [], kits: []),
            0,
            "An unknown baseline is not evidence of a change; it must not nag."
        )
    }

    func testNonReviewedDispositionsAreNotCountedAsChangedWork() {
        let store = UserDataStore(defaults: defaults)
        store.setReviewDisposition(.needsEdits, for: procedureFixture)

        let rewritten = procedureFixture(version: "2.0", steps: ["Different"])
        XCTAssertEqual(
            store.changedSinceReviewCount(procedures: [rewritten], rescueCards: [], kits: []),
            0,
            "Needs Edits is already queued work; it must not double-count."
        )
    }

    private var record: LocalReviewRecord {
        LocalReviewRecord(disposition: .reviewed, date: "2026-07-18")
    }

    private var procedureFixture: Procedure { procedureFixture(version: "1.0") }

    /// `steps` is material content (it feeds the review fingerprint); `tags`
    /// and `version` are editorial. The tests below rely on that split.
    private func procedureFixture(
        version: String,
        id: String = "central-line",
        steps: [String] = ["Prep and drape", "Insert under ultrasound"],
        tags: [String] = []
    ) -> Procedure {
        let json = """
        {
          "id": "\(id)",
          "title": "Central Venous Catheter",
          "category": "Vascular Access",
          "difficulty": "Advanced",
          "reviewTime": "3 min",
          "setting": ["ED"],
          "lastReviewed": "2026-07-18",
          "version": "\(version)",
          "tags": \(jsonArray(tags)),
          "visualAssets": null,
          "reviewerStatus": null,
          "sections": {
            "shiftMode": [],
            "indications": [],
            "contraindications": [],
            "anatomy": [],
            "equipment": ["Ultrasound"],
            "positioning": [],
            "steps": \(jsonArray(steps)),
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

    private func jsonArray(_ values: [String]) -> String {
        let encoded = try! JSONEncoder().encode(values)
        return String(decoding: encoded, as: UTF8.self)
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

    // MARK: - Quarantine

    /// Every persisted collection is one whole-blob key, loaded with `try?` and
    /// saved by rewriting the blob entirely. So a single undecodable record
    /// left the collection empty in memory, and the next sign-off wrote one
    /// record over all of them. Nothing crashed and nothing logged; the Review
    /// Center simply read 1 of 73 instead of 48.

    func testUndecodableReviewsAreSetAsideInsteadOfOverwritten() {
        let corrupt = Data("{not json at all".utf8)
        defaults.set(corrupt, forKey: "Procedures.locallyReviewedContent")

        let store = UserDataStore(defaults: defaults)

        XCTAssertTrue(store.hasUnreadableData, "the failure must be visible, not silent")
        XCTAssertTrue(store.unreadableDataKeys.contains("Procedures.locallyReviewedContent"))
        XCTAssertEqual(
            defaults.data(forKey: "Procedures.locallyReviewedContent.unreadable"), corrupt,
            "the original bytes must survive so the loss is recoverable"
        )
    }

    func testRecordingAReviewAfterAQuarantineStillWorks() {
        defaults.set(Data("{not json at all".utf8), forKey: "Procedures.locallyReviewedContent")
        let store = UserDataStore(defaults: defaults)

        // Refusing to write was the other obvious answer and is worse: it
        // leaves the app unable to record a review for as long as the bad blob
        // exists. The quarantine preserves the bytes and lets work continue.
        store.markReviewed(procedureFixture(version: "1.0", id: "cricothyrotomy"))

        XCTAssertEqual(store.localReviewRecord(for: procedureFixture(version: "1.0", id: "cricothyrotomy"))?.disposition, .reviewed)
        XCTAssertNotNil(defaults.data(forKey: "Procedures.locallyReviewedContent.unreadable"))
    }

    func testASecondBadLaunchDoesNotDestroyTheFirstQuarantine() {
        let original = Data("{the original corrupt blob".utf8)
        defaults.set(original, forKey: "Procedures.locallyReviewedContent")
        _ = UserDataStore(defaults: defaults)

        // A later launch finds a different bad blob. Overwriting the sidecar
        // would destroy the only surviving copy, which is the exact case this
        // mechanism exists to survive.
        defaults.set(Data("{a later, different corrupt blob".utf8), forKey: "Procedures.locallyReviewedContent")
        _ = UserDataStore(defaults: defaults)

        XCTAssertEqual(defaults.data(forKey: "Procedures.locallyReviewedContent.unreadable"), original)
    }

    func testCleanDataReportsNothingUnreadable() {
        let store = UserDataStore(defaults: defaults)
        XCTAssertFalse(store.hasUnreadableData)
        XCTAssertTrue(store.unreadableDataKeys.isEmpty)
    }

    func testLegacyDateOnlyReviewsStillMigrateRatherThanQuarantine() throws {
        defaults.set(
            try JSONEncoder().encode(["procedure:cricothyrotomy": "2026-01-14"]),
            forKey: "Procedures.locallyReviewedContent"
        )

        let store = UserDataStore(defaults: defaults)

        XCTAssertFalse(store.hasUnreadableData, "a known older format is not corruption")
        XCTAssertEqual(store.localReviewRecord(for: procedureFixture(version: "1.0", id: "cricothyrotomy"))?.date, "2026-01-14")
    }

    // MARK: - Badge policy memo

    /// The memo is keyed on library size and a review-map revision. This is the
    /// property that makes that key sound: recording a review must move the
    /// answer, and it only does if every mutation invalidates.
    func testBadgePolicyReflectsAReviewRecordedAfterItWasFirstComputed() {
        let store = UserDataStore(defaults: defaults)
        let library = (0..<4).map { procedureFixture(version: "1.0", id: "p\($0)") }

        XCTAssertEqual(store.badgePolicy(forProcedures: library), .suppressed, "0% reviewed")

        store.markReviewed(library[0])

        XCTAssertEqual(
            store.badgePolicy(forProcedures: library), .markReviewed,
            "a stale memo would still report .suppressed here"
        )
    }
}
