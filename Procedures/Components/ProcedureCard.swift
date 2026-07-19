import SwiftUI

struct ProcedureCard: View {
    let procedure: Procedure
    let isFavorite: Bool

    private var isAdvanced: Bool {
        procedure.difficulty == .advanced || procedure.difficulty == .rareCrash
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
                    if !procedure.reviewer.isClinicallyReviewed {
                        Image(systemName: "exclamationmark.shield")
                            .foregroundStyle(.orange)
                            .accessibilityLabel("Needs clinical review")
                    }
                    if isFavorite {
                        Image(systemName: "bookmark.fill")
                            .foregroundStyle(.blue)
                            .accessibilityLabel("Saved")
                    }
                    if isAdvanced {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundStyle(.orange)
                            .accessibilityLabel(procedure.difficulty.rawValue)
                    }
                }
                .font(.subheadline)
            }

            ProcedureTagRow(procedure: procedure)
        }
        .padding(.vertical, 6)
    }
}

/// Standard tag row for a procedure: difficulty, review time, and settings.
struct ProcedureTagRow: View {
    let procedure: Procedure

    private var tags: [String] {
        [procedure.difficulty.rawValue, procedure.reviewTime] + procedure.setting.map(\.rawValue)
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
            .foregroundStyle(.secondary)
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
