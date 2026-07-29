import XCTest
@testable import Procedures

/// Locks the one rule that the app got wrong everywhere except the Review
/// Center: review state is the reconciliation of two records — what shipped in
/// the content, and what the reader signed off on this device — and every
/// surface must read the same answer.
///
/// The reported symptom was a procedure the clinician had reviewed still
/// announcing "DRAFT — not clinically reviewed" on its own detail page, because
/// that page asked the bundled content and never the reader's record.
@MainActor
final class ReviewStateTests: XCTestCase {
    private var suiteNames: [String] = []

    override func tearDownWithError() throws {
        for suiteName in suiteNames {
            UserDefaults().removePersistentDomain(forName: suiteName)
        }
        suiteNames = []
        try super.tearDownWithError()
    }

    // MARK: - Reconciliation

    func testLocalSignOffOnUnreviewedContentReadsAsReviewed() {
        let state = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .reviewed, date: "2026-07-29"),
            contentState: .unchanged
        )

        XCTAssertEqual(state, .reviewedLocally(date: "2026-07-29"))
        XCTAssertTrue(state.isReviewed)
        XCTAssertFalse(state.isCautionary)
    }

    /// The exact string from the bug report must not survive a sign-off.
    func testDetailLabelStopsSayingDraftOnceReviewedLocally() {
        let unreviewed = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: nil,
            contentState: nil
        )
        XCTAssertEqual(unreviewed.detailLabel(source: .aiDraft), "DRAFT — not reviewed")

        let reviewed = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .reviewed, date: "2026-07-29"),
            contentState: .unchanged
        )
        XCTAssertFalse(reviewed.detailLabel(source: .aiDraft).contains("DRAFT"))
        XCTAssertEqual(reviewed.detailLabel(source: .aiDraft), "Reviewed · 2026-07-29")
    }

    /// Single-user app: a review reads "Reviewed" with no attribution, and
    /// reviewed content reads identically whoever signed it off.
    func testReviewedContentReadsTheSameFromEitherSource() {
        let local = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .reviewed, date: "2026-07-29"),
            contentState: .unchanged
        )
        let upstream = ReviewState.resolve(sourceStatus: .externallyReviewed, record: nil, contentState: nil)

        XCTAssertEqual(local.shortLabel, "Reviewed")
        XCTAssertEqual(upstream.shortLabel, "Reviewed")
        for label in [local.shortLabel, upstream.shortLabel, local.detailLabel(source: .aiDraft)] {
            XCTAssertFalse(label.lowercased().contains("you"), label)
        }
    }

    /// The labels collapse, but the states must not. Export refuses to promote a
    /// sign-off the repo already carries, and the validator treats the two
    /// differently, so the distinction has to survive underneath the copy.
    func testLocalAndUpstreamRemainDistinctStatesDespiteIdenticalCopy() {
        let local = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .reviewed, date: "2026-07-29"),
            contentState: .unchanged
        )

        XCTAssertNotEqual(local, .clinicallyReviewed)
        XCTAssertEqual(local, .reviewedLocally(date: "2026-07-29"))
    }

    func testChangedContentMarksTheReviewOutOfDateWithoutRevokingIt() {
        let state = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .reviewed, date: "2026-01-01"),
            contentState: .materialChanged
        )

        XCTAssertEqual(state, .reviewedLocallyOutdated(date: "2026-01-01"))
        XCTAssertTrue(state.isReviewed, "a review is the reader's work and is not revoked by a later edit")
        XCTAssertTrue(state.isCautionary)
    }

    /// An unknown baseline is an unknown, not a problem. Pre-fingerprint records
    /// must not be downgraded to "out of date".
    func testUnknownBaselineIsTreatedAsCurrent() {
        let state = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .reviewed, date: "2025-05-01"),
            contentState: .unknownBaseline
        )

        XCTAssertEqual(state, .reviewedLocally(date: "2025-05-01"))
    }

    func testReaderFlagOutranksAnUpstreamSignOff() {
        let state = ReviewState.resolve(
            sourceStatus: .externallyReviewed,
            record: LocalReviewRecord(disposition: .needsEdits, date: "2026-07-29"),
            contentState: .unchanged
        )

        XCTAssertEqual(state, .flaggedForEdits)
        XCTAssertFalse(state.isReviewed)
    }

    func testDeferringIsNotAReview() {
        let state = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .deferred, date: "2026-07-29"),
            contentState: .unchanged
        )

        XCTAssertEqual(state, .unreviewed)
        XCTAssertFalse(state.isReviewed)
    }

    func testUpstreamSignOffStandsOnItsOwn() {
        let state = ReviewState.resolve(
            sourceStatus: .externallyReviewed,
            record: nil,
            contentState: nil
        )

        XCTAssertEqual(state, .clinicallyReviewed)
        XCTAssertTrue(state.isReviewed)
    }

    // MARK: - Badge policy

    func testBadgeIsSuppressedWhenNothingIsReviewed() {
        XCTAssertEqual(ReviewBadgePolicy.make(reviewedCount: 0, total: 55), .suppressed)
    }

    /// Marking 100% of rows is the same non-information as marking 0%.
    func testBadgeIsSuppressedWhenEverythingIsReviewed() {
        XCTAssertEqual(ReviewBadgePolicy.make(reviewedCount: 55, total: 55), .suppressed)
    }

    func testBadgeMarksTheReviewedMinority() {
        XCTAssertEqual(ReviewBadgePolicy.make(reviewedCount: 1, total: 55), .markReviewed)
        XCTAssertEqual(ReviewBadgePolicy.make(reviewedCount: 27, total: 55), .markReviewed)
    }

    func testBadgeFlipsToMarkingTheUnreviewedMinority() {
        XCTAssertEqual(ReviewBadgePolicy.make(reviewedCount: 54, total: 55), .markUnreviewed)
    }

    func testEmptyLibraryDoesNotBadge() {
        XCTAssertEqual(ReviewBadgePolicy.make(reviewedCount: 0, total: 0), .suppressed)
    }

    /// Personal states are always a minority and always actionable, so they show
    /// regardless of which way the corpus-wide policy is pointing.
    func testPersonalStatesAlwaysBadge() {
        for policy in [ReviewBadgePolicy.suppressed, .markReviewed, .markUnreviewed] {
            XCTAssertTrue(policy.shouldBadge(.flaggedForEdits), "\(policy)")
            XCTAssertTrue(policy.shouldBadge(.reviewedLocallyOutdated(date: "2026-01-01")), "\(policy)")
        }
    }

    func testSuppressedPolicyBadgesNeitherBulkState() {
        XCTAssertFalse(ReviewBadgePolicy.suppressed.shouldBadge(.unreviewed))
        XCTAssertFalse(ReviewBadgePolicy.suppressed.shouldBadge(.clinicallyReviewed))
        XCTAssertFalse(ReviewBadgePolicy.suppressed.shouldBadge(.reviewedLocally(date: "2026-01-01")))
    }

    // MARK: - End to end through the store

    /// The whole reported defect in one assertion: sign a procedure off, and the
    /// answer every screen reads must change.
    func testSigningOffChangesWhatTheAppReports() {
        let procedure = makeProcedure()
        let userData = makeUserDataStore()

        XCTAssertEqual(userData.reviewState(for: procedure), .unreviewed)
        XCTAssertEqual(userData.effectiveReviewedCount(procedures: [procedure]), 0)

        userData.markReviewed(procedure)

        XCTAssertTrue(userData.reviewState(for: procedure).isReviewed)
        XCTAssertEqual(userData.effectiveReviewedCount(procedures: [procedure]), 1)
    }

    /// The corpus notice ("nothing in this library has been reviewed") is keyed
    /// on this count. It kept firing at a reader who had reviewed something
    /// because it asked the bundled status only.
    func testCorpusCountSeesLocalReviews() {
        let reviewed = makeProcedure(id: "cricothyrotomy")
        let others = (0..<9).map { makeProcedure(id: "other-\($0)") }
        let userData = makeUserDataStore()

        userData.markReviewed(reviewed)

        let corpus = [reviewed] + others
        XCTAssertEqual(userData.effectiveReviewedCount(procedures: corpus), 1)
        XCTAssertEqual(userData.badgePolicy(forProcedures: corpus), .markReviewed)
    }

    /// An item carrying both an upstream sign-off and a local one is one
    /// reviewed item, not two. Without this the progress count could exceed the
    /// library size once `apply_local_reviews.py` promotes a batch.
    func testAnItemReviewedTwiceIsCountedOnce() {
        let procedure = makeProcedure(reviewerStatus: .externallyReviewed)
        let userData = makeUserDataStore()
        userData.markReviewed(procedure)

        XCTAssertEqual(userData.effectiveReviewedCount(procedures: [procedure]), 1)
    }

    /// Editing an already-reviewed procedure re-baselines the review, so it must
    /// stay clean rather than flipping to "out of date" over a deliberate local
    /// correction — and the original review date must survive, because this
    /// re-points the baseline rather than re-dating the work.
    ///
    /// Note what is deliberately *not* asserted: that the edited copy and the
    /// pre-edit copy read the same. After a re-baseline they correctly differ,
    /// because the stale copy no longer matches the recorded fingerprint. An
    /// earlier version of this test asserted that equality and CI caught it.
    func testALocalEditDoesNotAgeTheReviewOfIt() {
        let procedure = makeProcedure()
        let userData = makeUserDataStore()
        userData.markReviewed(procedure)
        let originalDate = userData.localReviewRecord(for: procedure)?.date
        XCTAssertNotNil(originalDate)

        var edited = procedure
        edited.sections.steps = ["a corrected step"]
        userData.rebaselineReviewAfterLocalEdit(
            for: edited,
            previousFingerprint: procedure.materialFingerprint
        )

        let state = userData.reviewState(for: edited)
        XCTAssertFalse(state.isCautionary, "a deliberate edit must not flag the review that preceded it")
        XCTAssertEqual(state, .reviewedLocally(date: originalDate ?? ""))
        XCTAssertEqual(userData.localReviewRecord(for: edited)?.date, originalDate)
    }

    // MARK: - Nothing forgets

    /// Marking one procedure reviewed has to move every derived answer in the
    /// app at once. These are the exact predicates the screens use, asserted
    /// side by side, because the original bug was not that any single one was
    /// wrong — it was that they disagreed with each other.
    func testOneSignOffMovesEveryDerivedAnswer() {
        let target = makeProcedure(id: "cricothyrotomy")
        let corpus = [target] + (0..<9).map { makeProcedure(id: "other-\($0)") }
        let userData = makeUserDataStore()

        // Before: every surface says unreviewed.
        XCTAssertFalse(userData.reviewState(for: target).isReviewed, "detail header / row badge")
        XCTAssertEqual(userData.effectiveReviewedCount(procedures: corpus), 0, "corpus notice predicate")
        XCTAssertEqual(userData.badgePolicy(forProcedures: corpus), .suppressed, "row badge policy")
        XCTAssertNil(userData.localReviewRecord(for: target), "Review Center row")
        XCTAssertEqual(userData.localReviewCount(procedures: corpus, rescueCards: [], kits: []), 0, "Review Center count")

        userData.markReviewed(target)

        // After: all of them, together.
        XCTAssertTrue(userData.reviewState(for: target).isReviewed, "detail header / row badge")
        XCTAssertEqual(userData.effectiveReviewedCount(procedures: corpus), 1, "corpus notice predicate")
        XCTAssertEqual(userData.badgePolicy(forProcedures: corpus), .markReviewed, "row badge policy")
        XCTAssertEqual(userData.localReviewRecord(for: target)?.disposition, .reviewed, "Review Center row")
        XCTAssertEqual(userData.localReviewCount(procedures: corpus, rescueCards: [], kits: []), 1, "Review Center count")

        // Untouched neighbours must not drift with it.
        for other in corpus.dropFirst() {
            XCTAssertFalse(userData.reviewState(for: other).isReviewed, other.id)
        }
    }

    /// The Review Center's "Reviewed" count and the list that row opens
    /// filter on different expressions. They must never disagree, or a reader
    /// taps a count of 1 and lands on an empty screen.
    func testTheReviewedCountMatchesTheListItOpens() {
        let corpus = (0..<5).map { makeProcedure(id: "p-\($0)") }
        let userData = makeUserDataStore()
        userData.markReviewed(corpus[1])
        userData.setReviewDisposition(.needsEdits, for: corpus[2])
        userData.setReviewDisposition(.deferred, for: corpus[3])

        let count = userData.localReviewCount(procedures: corpus, rescueCards: [], kits: [])
        let listed = corpus.filter { userData.localReviewRecord(for: $0)?.disposition == .reviewed }

        XCTAssertEqual(count, listed.count)
        XCTAssertEqual(listed.map(\.id), ["p-1"])
    }

    /// Rescue cards and kits carry the same review machinery. Reviewing one must
    /// behave identically to reviewing a procedure — the earlier bug reached all
    /// three content kinds because they all read the bundled status.
    func testRescueCardsAndKitsSignOffTheSameWay() {
        let card = makeRescueCard()
        let kit = makeKit()
        let userData = makeUserDataStore()

        XCTAssertEqual(userData.reviewState(for: card), .unreviewed)
        XCTAssertEqual(userData.reviewState(for: kit), .unreviewed)

        userData.markReviewed(card)
        userData.markReviewed(kit)

        XCTAssertTrue(userData.reviewState(for: card).isReviewed)
        XCTAssertTrue(userData.reviewState(for: kit).isReviewed)
        XCTAssertEqual(userData.effectiveReviewedCount(rescueCards: [card]), 1)
        XCTAssertEqual(userData.effectiveReviewedCount(kits: [kit]), 1)
    }

    /// Clearing every mark from Settings has to walk the app back just as
    /// completely as signing off walked it forward.
    func testClearingAllReviewsWalksEverythingBack() {
        let procedure = makeProcedure()
        let card = makeRescueCard()
        let kit = makeKit()
        let userData = makeUserDataStore()
        userData.markReviewed(procedure)
        userData.markReviewed(card)
        userData.markReviewed(kit)

        userData.clearAllLocalReviews()

        XCTAssertEqual(userData.reviewState(for: procedure), .unreviewed)
        XCTAssertEqual(userData.reviewState(for: card), .unreviewed)
        XCTAssertEqual(userData.reviewState(for: kit), .unreviewed)
        XCTAssertEqual(userData.effectiveReviewedCount(procedures: [procedure]), 0)
    }

    /// A sign-off has to survive the app being killed. It is written to defaults
    /// on every mutation; a store rebuilt on the same suite must see it.
    func testASignOffSurvivesARelaunch() {
        let procedure = makeProcedure()
        let suiteName = "ReviewStateTests.\(UUID().uuidString)"
        suiteNames.append(suiteName)
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)

        UserDataStore(defaults: defaults).markReviewed(procedure)

        let relaunched = UserDataStore(defaults: defaults)
        XCTAssertTrue(relaunched.reviewState(for: procedure).isReviewed)
    }

    // MARK: - Fixtures

    private func makeUserDataStore() -> UserDataStore {
        let suiteName = "ReviewStateTests.\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)
        suiteNames.append(suiteName)
        return UserDataStore(defaults: defaults)
    }

    private func makeRescueCard(id: String = "rescue-test") -> ComplicationRescueCard {
        ComplicationRescueCard(
            id: id,
            title: "Test Rescue Card",
            acuity: .crash,
            relatedProcedureIDs: [],
            trigger: ["a"],
            immediateMoves: ["a", "b"],
            reassess: ["a"],
            avoid: ["a"],
            tags: ["test"],
            lastReviewed: "2026-01-01",
            version: "1.0",
            references: ["Smith et al. 2024"],
            reviewerStatus: .needsClinicalReview,
            contentSource: .aiDraft
        )
    }

    private func makeKit(id: String = "kit-test") -> Kit {
        Kit(
            id: id,
            title: "Test Kit",
            subtitle: "Test",
            category: .other,
            relatedProcedureIDs: [],
            tags: ["test"],
            lastReviewed: "2026-01-01",
            version: "1.0",
            reviewerStatus: .needsClinicalReview,
            contentSource: .aiDraft,
            inKit: ["a"],
            outsideKit: ["b"],
            commonlyForgotten: ["c"],
            patientSetup: ["d"],
            sterileSetup: ["e"],
            backupEquipment: ["f"],
            references: ["Smith et al. 2024"]
        )
    }

    private func makeProcedure(
        id: String = "test",
        reviewerStatus: ReviewerStatus = .needsClinicalReview
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
            dosing: nil,
            reviewerStatus: reviewerStatus,
            contentSource: .aiDraft,
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
                references: ["Smith et al. 2024"]
            )
        )
    }
}
