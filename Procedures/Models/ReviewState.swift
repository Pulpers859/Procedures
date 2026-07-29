import SwiftUI

/// The single answer to "has this been reviewed?"
///
/// The app has two independent records of review: the `reviewerStatus` bundled
/// with the content, and the clinician's own sign-off stored on the device.
/// Every bedside surface used to read only the first and the Review Center read
/// only the second, so signing off a procedure updated one screen and left the
/// detail page still reading "DRAFT — not clinically reviewed" about content the
/// reader had personally reviewed an hour earlier. That contradiction is worse
/// than either label alone: it teaches the reader that the review banner is
/// noise.
///
/// This type is the only place the two records are reconciled. Nothing in the UI
/// should branch on `reviewer.isClinicallyReviewed` directly.
///
/// This is a single-user app, so the UI never attributes a review back to the
/// reader — a sign-off simply reads "Reviewed". The local/upstream distinction
/// is kept in the case names because it still drives real behaviour: promoting a
/// local review into the content's actual status is a repo operation
/// (`scripts/apply_local_reviews.py`), not something the app can do to itself.
enum ReviewState: Hashable {
    /// No sign-off from either source. Also covers a deferred item: deferring is
    /// declining to decide, which is not a review.
    case unreviewed
    /// The reader marked this as needing edits. Their own flag outranks
    /// everything else, including an upstream sign-off.
    case flaggedForEdits
    /// The reader signed this off and the material content is what they read.
    case reviewedLocally(date: String)
    /// The reader signed this off, but steps/doses/contraindications have moved
    /// since. The review still stands — this only says it is worth a second look.
    case reviewedLocallyOutdated(date: String)
    /// The bundled content carries a clinical sign-off.
    case clinicallyReviewed

    /// Reconciles the bundled status with the device's own record.
    ///
    /// Order is deliberate and monotone in caution: the reader's "needs edits"
    /// wins outright, a formal clinical sign-off outranks a personal one, and
    /// anything unaccounted for falls through to `unreviewed`.
    static func resolve(
        sourceStatus: ReviewerStatus,
        record: LocalReviewRecord?,
        contentState: ReviewContentState?
    ) -> ReviewState {
        if record?.disposition == .needsEdits {
            return .flaggedForEdits
        }
        if sourceStatus.isClinicallyReviewed {
            return .clinicallyReviewed
        }
        if let record, record.disposition == .reviewed {
            return contentState == .materialChanged
                ? .reviewedLocallyOutdated(date: record.date)
                : .reviewedLocally(date: record.date)
        }
        return .unreviewed
    }

    /// True when a reader has vouched for this content, from either source. An
    /// outdated review still counts: a review is the reader's work and is never
    /// revoked by a later content change.
    var isReviewed: Bool {
        switch self {
        case .reviewedLocally, .reviewedLocallyOutdated, .clinicallyReviewed:
            return true
        case .unreviewed, .flaggedForEdits:
            return false
        }
    }

    /// True when the state is something the reader should act on before relying
    /// on the content.
    var isCautionary: Bool {
        switch self {
        case .unreviewed, .flaggedForEdits, .reviewedLocallyOutdated:
            return true
        case .reviewedLocally, .clinicallyReviewed:
            return false
        }
    }

    var systemImage: String {
        switch self {
        case .unreviewed: return "exclamationmark.shield"
        case .flaggedForEdits: return "square.and.pencil"
        case .reviewedLocally: return "checkmark.seal.fill"
        case .reviewedLocallyOutdated: return "arrow.triangle.2.circlepath"
        case .clinicallyReviewed: return "checkmark.seal.fill"
        }
    }

    /// Chip text. Short enough to sit beside a title on a list row.
    var shortLabel: String {
        switch self {
        case .unreviewed: return "Not reviewed"
        case .flaggedForEdits: return "Needs edits"
        case .reviewedLocally: return "Reviewed"
        case .reviewedLocallyOutdated: return "Review out of date"
        case .clinicallyReviewed: return "Reviewed"
        }
    }

    /// Header text for a detail page, where a date fits and there is one item to
    /// describe rather than fifty.
    func detailLabel(source: ContentSource) -> String {
        switch self {
        case .unreviewed:
            return source == .aiDraft ? "DRAFT — not reviewed" : "Not reviewed"
        case .flaggedForEdits:
            return "Needs edits"
        case .reviewedLocally(let date):
            return "Reviewed · \(date)"
        case .reviewedLocallyOutdated(let date):
            return "Review out of date · reviewed \(date)"
        case .clinicallyReviewed:
            return "Reviewed"
        }
    }

    var tint: Color {
        switch self {
        case .unreviewed, .flaggedForEdits, .reviewedLocallyOutdated:
            return AppSemanticColor.warningText
        case .reviewedLocally, .clinicallyReviewed:
            return .green
        }
    }
}

/// Which review state, if either, is worth badging on a list row.
///
/// A badge that appears on every row distinguishes nothing and costs real
/// visual weight — 55 identical orange shields is alarm fatigue, not a warning.
/// The rule is to mark the minority and leave the majority as the unmarked
/// default, which keeps the badge informative through the whole life of the
/// library: nothing reviewed, a few reviewed, most reviewed, all reviewed.
enum ReviewBadgePolicy: Hashable {
    /// Every row would carry the same mark. Say it once in the list header and
    /// on the detail page instead.
    case suppressed
    /// Reviewed items are the exception, so mark those.
    case markReviewed
    /// Unreviewed items are the exception, so mark those.
    case markUnreviewed

    static func make(reviewedCount: Int, total: Int) -> ReviewBadgePolicy {
        guard total > 0, reviewedCount > 0, reviewedCount < total else { return .suppressed }
        return reviewedCount * 2 <= total ? .markReviewed : .markUnreviewed
    }

    /// Whether this particular row earns a badge under the policy. States the
    /// reader created themselves (`flaggedForEdits`, an out-of-date review) always
    /// show: they are personal, always a minority, and always actionable.
    func shouldBadge(_ state: ReviewState) -> Bool {
        switch state {
        case .flaggedForEdits, .reviewedLocallyOutdated:
            return true
        case .reviewedLocally, .clinicallyReviewed:
            return self == .markReviewed
        case .unreviewed:
            return self == .markUnreviewed
        }
    }
}

/// Compact review mark for a list row. Silhouette differs by state, so it does
/// not rely on colour alone.
struct ReviewStateBadge: View {
    let state: ReviewState
    let policy: ReviewBadgePolicy

    var body: some View {
        if policy.shouldBadge(state) {
            Image(systemName: state.systemImage)
                .foregroundStyle(state.tint)
                .accessibilityLabel(state.shortLabel)
        }
    }
}

/// Review state as it appears at the top of a detail page, where it is always
/// shown — a reader must never open an item without being told where it stands.
struct ReviewStateChip: View {
    let state: ReviewState
    let source: ContentSource
    var alignment: TextAlignment = .trailing

    var body: some View {
        Label(state.detailLabel(source: source), systemImage: state.systemImage)
            .font(.caption.weight(.semibold))
            .foregroundStyle(state.tint)
            .multilineTextAlignment(alignment)
            .fixedSize(horizontal: false, vertical: true)
    }
}
