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
/// It never overstates: a local sign-off is attributed to the reader ("Reviewed
/// by you"), never promoted into a claim of formal clinical review. Turning a
/// local review into the content's actual status is a repo operation
/// (`scripts/apply_local_reviews.py`), not something the app can do to itself.
enum ReviewState: Hashable {
    /// No sign-off from either source. Also covers a deferred item: deferring is
    /// declining to decide, which is not a review.
    case unreviewed
    /// The reader marked this as needing edits. Their own flag outranks
    /// everything else, including an upstream sign-off.
    case flaggedByYou
    /// The reader signed this off and the material content is what they read.
    case reviewedByYou(date: String)
    /// The reader signed this off, but steps/doses/contraindications have moved
    /// since. The review still stands — this only says it is worth a second look.
    case reviewedByYouOutdated(date: String)
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
            return .flaggedByYou
        }
        if sourceStatus.isClinicallyReviewed {
            return .clinicallyReviewed
        }
        if let record, record.disposition == .reviewed {
            return contentState == .materialChanged
                ? .reviewedByYouOutdated(date: record.date)
                : .reviewedByYou(date: record.date)
        }
        return .unreviewed
    }

    /// True when a reader has vouched for this content, from either source. An
    /// outdated review still counts: a review is the reader's work and is never
    /// revoked by a later content change.
    var isReviewed: Bool {
        switch self {
        case .reviewedByYou, .reviewedByYouOutdated, .clinicallyReviewed:
            return true
        case .unreviewed, .flaggedByYou:
            return false
        }
    }

    /// True when the state is something the reader should act on before relying
    /// on the content.
    var isCautionary: Bool {
        switch self {
        case .unreviewed, .flaggedByYou, .reviewedByYouOutdated:
            return true
        case .reviewedByYou, .clinicallyReviewed:
            return false
        }
    }

    var systemImage: String {
        switch self {
        case .unreviewed: return "exclamationmark.shield"
        case .flaggedByYou: return "square.and.pencil"
        case .reviewedByYou: return "checkmark.seal.fill"
        case .reviewedByYouOutdated: return "arrow.triangle.2.circlepath"
        case .clinicallyReviewed: return "checkmark.seal.fill"
        }
    }

    /// Chip text. Short enough to sit beside a title on a list row.
    var shortLabel: String {
        switch self {
        case .unreviewed: return "Not reviewed"
        case .flaggedByYou: return "Needs edits"
        case .reviewedByYou: return "Reviewed by you"
        case .reviewedByYouOutdated: return "Review out of date"
        case .clinicallyReviewed: return "Clinically reviewed"
        }
    }

    /// Header text for a detail page, where the extra clause fits and the reader
    /// has committed to this one item.
    func detailLabel(source: ContentSource) -> String {
        switch self {
        case .unreviewed:
            return source == .aiDraft ? "DRAFT — not clinically reviewed" : "Not reviewed"
        case .flaggedByYou:
            return "You flagged this for edits"
        case .reviewedByYou(let date):
            return "Reviewed by you · \(date)"
        case .reviewedByYouOutdated(let date):
            return "Your review (\(date)) predates a content change"
        case .clinicallyReviewed:
            return "Clinically reviewed"
        }
    }

    var tint: Color {
        switch self {
        case .unreviewed, .flaggedByYou, .reviewedByYouOutdated:
            return AppSemanticColor.warningText
        case .reviewedByYou, .clinicallyReviewed:
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
    /// reader created themselves (`flaggedByYou`, an out-of-date review) always
    /// show: they are personal, always a minority, and always actionable.
    func shouldBadge(_ state: ReviewState) -> Bool {
        switch state {
        case .flaggedByYou, .reviewedByYouOutdated:
            return true
        case .reviewedByYou, .clinicallyReviewed:
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
