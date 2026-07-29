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

        XCTAssertEqual(state, .reviewedByYou(date: "2026-07-29"))
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
        XCTAssertEqual(unreviewed.detailLabel(source: .aiDraft), "DRAFT — not clinically reviewed")

        let reviewed = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .reviewed, date: "2026-07-29"),
            contentState: .unchanged
        )
        XCTAssertFalse(reviewed.detailLabel(source: .aiDraft).contains("DRAFT"))
        XCTAssertEqual(reviewed.detailLabel(source: .aiDraft), "Reviewed by you · 2026-07-29")
    }

    /// A local sign-off is attributed to the reader and never promoted into a
    /// claim of formal clinical review. Only the repo can do that.
    func testLocalSignOffNeverClaimsClinicalReview() {
        let state = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .reviewed, date: "2026-07-29"),
            contentState: .unchanged
        )

        XCTAssertNotEqual(state, .clinicallyReviewed)
        XCTAssertFalse(state.shortLabel.lowercased().contains("clinically"))
    }

    func testChangedContentMarksTheReviewOutOfDateWithoutRevokingIt() {
        let state = ReviewState.resolve(
            sourceStatus: .needsClinicalReview,
            record: LocalReviewRecord(disposition: .reviewed, date: "2026-01-01"),
            contentState: .materialChanged
        )

        XCTAssertEqual(state, .reviewedByYouOutdated(date: "2026-01-01"))
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

        XCTAssertEqual(state, .reviewedByYou(date: "2025-05-01"))
    }

    func testReaderFlagOutranksAnUpstreamSignOff() {
        let state = ReviewState.resolve(
            sourceStatus: .externallyReviewed,
            record: LocalReviewRecord(disposition: .needsEdits, date: "2026-07-29"),
            contentState: .unchanged
        )

        XCTAssertEqual(state, .flaggedByYou)
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
            XCTAssertTrue(policy.shouldBadge(.flaggedByYou), "\(policy)")
            XCTAssertTrue(policy.shouldBadge(.reviewedByYouOutdated(date: "2026-01-01")), "\(policy)")
        }
    }

    func testSuppressedPolicyBadgesNeitherBulkState() {
        XCTAssertFalse(ReviewBadgePolicy.suppressed.shouldBadge(.unreviewed))
        XCTAssertFalse(ReviewBadgePolicy.suppressed.shouldBadge(.clinicallyReviewed))
        XCTAssertFalse(ReviewBadgePolicy.suppressed.shouldBadge(.reviewedByYou(date: "2026-01-01")))
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

    /// Editing a procedure you already signed off re-baselines the review, so
    /// the state must stay clean rather than flipping to "out of date" over your
    /// own correction.
    func testYourOwnEditDoesNotAgeYourReview() {
        let procedure = makeProcedure()
        let userData = makeUserDataStore()
        userData.markReviewed(procedure)

        var edited = procedure
        edited.sections.steps = ["a step I just corrected"]
        userData.rebaselineReviewAfterLocalEdit(for: edited)

        XCTAssertEqual(userData.reviewState(for: edited), userData.reviewState(for: procedure))
        XCTAssertFalse(userData.reviewState(for: edited).isCautionary)
    }

    // MARK: - Fixtures

    private func makeUserDataStore() -> UserDataStore {
        let suiteName = "ReviewStateTests.\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)
        suiteNames.append(suiteName)
        return UserDataStore(defaults: defaults)
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
