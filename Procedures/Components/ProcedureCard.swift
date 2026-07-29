import SwiftUI

struct ProcedureCard: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure
    let isFavorite: Bool

    private var reviewState: ReviewState {
        userData.reviewState(for: procedure)
    }

    private var badgePolicy: ReviewBadgePolicy {
        userData.badgePolicy(forProcedures: repository.procedures)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline, spacing: 10) {
                VStack(alignment: .leading, spacing: 3) {
                    Text(procedure.title)
                        .font(.headline)
                        .foregroundStyle(.primary)
                    Text(procedure.category.rawValue)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                Spacer(minLength: 8)
                HStack(spacing: 8) {
                    // Marks whichever review state is the minority, so the badge
                    // stays informative instead of appearing on every row. See
                    // ReviewBadgePolicy.
                    ReviewStateBadge(state: reviewState, policy: badgePolicy)
                    if isFavorite {
                        Image(systemName: "bookmark.fill")
                            .foregroundStyle(.blue)
                    }
                    // The risk triangle said the same thing as the difficulty
                    // chip directly beneath it, in a louder voice, on two rows
                    // out of every three. The chip carries it alone now.
                }
                .font(.subheadline)
                .accessibilityHidden(true)
            }

            ProcedureTagRow(procedure: procedure)
        }
        .padding(.vertical, 6)
        // This is the most-repeated row in the app. Ungrouped it read as 8-9
        // separate swipes with difficulty announced twice; one curated label
        // keeps scanning a 55-item list workable under VoiceOver.
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(accessibilityDescription)
    }

    private var accessibilityDescription: String {
        var parts = [procedure.title, procedure.category.rawValue, procedure.difficulty.rawValue]
        parts.append("\(procedure.reviewTime) review")
        if !procedure.setting.isEmpty {
            parts.append(procedure.setting.map(\.rawValue).joined(separator: ", "))
        }
        // Mirrors the badge exactly. When the badge is suppressed the state is
        // identical on every row and is disclosed once in the list header, which
        // VoiceOver reads on the way in — repeating it 55 times would bury the
        // titles the reader is actually scanning for.
        if badgePolicy.shouldBadge(reviewState) { parts.append(reviewState.shortLabel) }
        if isFavorite { parts.append("Saved") }
        return parts.joined(separator: ". ")
    }
}

/// Compact tag row for a procedure: difficulty and review time.
///
/// Settings used to be appended here too, which put four chips on every row
/// and produced runs of consecutive rows reading "Advanced / standard / ED /
/// Trauma" identically - weight without information. Settings remain on the
/// detail page, where there is one procedure to describe rather than fifty.
struct ProcedureTagRow: View {
    let procedure: Procedure

    private var tags: [String] {
        [procedure.difficulty.rawValue, procedure.reviewTime]
    }

    var body: some View {
        FlowTagView(tags: tags)
    }
}

struct TagView: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.caption.weight(.semibold))
            .padding(.horizontal, 10)
            .padding(.vertical, 5)
            // These tags carry difficulty and review time — the risk signal a
            // clinician triages on. .secondary over a tinted fill lands under
            // AA at caption size; the fill alone already reads as a chip.
            .foregroundStyle(.primary)
            .background(Color(.tertiarySystemFill), in: Capsule())
            .lineLimit(2)
            .multilineTextAlignment(.leading)
    }
}

/// Tags that wrap onto multiple rows naturally instead of collapsing to a
/// single vertical column. Uses a real flow layout so spacing stays even.
struct FlowTagView: View {
    let tags: [String]
    var spacing: CGFloat = 6
    var lineSpacing: CGFloat = 6

    var body: some View {
        FlowLayout(spacing: spacing, lineSpacing: lineSpacing) {
            ForEach(Array(tags.enumerated()), id: \.offset) { _, tag in
                TagView(text: tag)
            }
        }
    }
}

/// A simple left-aligned flow layout that wraps subviews onto new lines when
/// they run out of horizontal space.
struct FlowLayout: Layout {
    var spacing: CGFloat = 6
    var lineSpacing: CGFloat = 6

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout Void) -> CGSize {
        let maxWidth = proposal.width ?? .infinity
        var rowWidth: CGFloat = 0
        var rowHeight: CGFloat = 0
        var totalWidth: CGFloat = 0
        var totalHeight: CGFloat = 0

        for subview in subviews {
            let size = measuredSize(for: subview, maxWidth: maxWidth)
            if rowWidth > 0, rowWidth + spacing + size.width > maxWidth {
                totalWidth = max(totalWidth, rowWidth)
                totalHeight += rowHeight + lineSpacing
                rowWidth = size.width
                rowHeight = size.height
            } else {
                rowWidth += (rowWidth > 0 ? spacing : 0) + size.width
                rowHeight = max(rowHeight, size.height)
            }
        }
        totalWidth = max(totalWidth, rowWidth)
        totalHeight += rowHeight

        let resolvedWidth = maxWidth.isFinite ? maxWidth : totalWidth
        return CGSize(width: resolvedWidth, height: totalHeight)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout Void) {
        var x = bounds.minX
        var y = bounds.minY
        var rowHeight: CGFloat = 0

        for subview in subviews {
            let size = measuredSize(for: subview, maxWidth: bounds.width)
            if x > bounds.minX, x + size.width > bounds.maxX {
                x = bounds.minX
                y += rowHeight + lineSpacing
                rowHeight = 0
            }
            subview.place(at: CGPoint(x: x, y: y), anchor: .topLeading, proposal: ProposedViewSize(size))
            x += size.width + spacing
            rowHeight = max(rowHeight, size.height)
        }
    }

    private func measuredSize(for subview: LayoutSubview, maxWidth: CGFloat) -> CGSize {
        let ideal = subview.sizeThatFits(.unspecified)
        guard maxWidth.isFinite, ideal.width > maxWidth else { return ideal }
        return subview.sizeThatFits(ProposedViewSize(width: maxWidth, height: nil))
    }
}
