import SwiftUI

struct SectionCard<Content: View>: View {
    let title: String
    var systemImage: String? = nil
    var miniHeight: CGFloat? = nil
    let content: Content

    init(
        title: String,
        systemImage: String? = nil,
        miniHeight: CGFloat? = nil,
        @ViewBuilder content: () -> Content
    ) {
        self.title = title
        self.systemImage = systemImage
        self.miniHeight = miniHeight
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                if let systemImage {
                    Image(systemName: systemImage)
                        .foregroundStyle(.blue)
                        .accessibilityHidden(true)
                }
                Text(title)
                    .font(.headline)
                Spacer()
            }
            content
        }
        .padding()
        .frame(maxWidth: .infinity, minHeight: miniHeight, alignment: .topLeading)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(.secondary.opacity(0.12), lineWidth: 1)
        )
    }
}

struct BulletListView: View {
    let items: [String]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(Array(items.enumerated()), id: \.offset) { _, item in
                HStack(alignment: .top, spacing: 8) {
                    Text("•")
                        .font(.body.weight(.bold))
                        .foregroundStyle(.blue)
                    Text(item)
                        .font(.body)
                        .fixedSize(horizontal: false, vertical: true)
                        .textSelection(.enabled)
                }
            }
        }
    }
}

struct NumberedListView: View {
    let items: [String]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(Array(items.enumerated()), id: \.offset) { index, item in
                HStack(alignment: .top, spacing: 10) {
                    Text("\(index + 1).")
                        .font(.body.weight(.bold))
                        .foregroundStyle(.blue)
                        .monospacedDigit()
                        .frame(width: 30, alignment: .leading)
                    Text(item)
                        .font(.body)
                        .fixedSize(horizontal: false, vertical: true)
                        .textSelection(.enabled)
                }
            }
        }
    }
}

struct MetadataRow: View {
    let icon: String
    let title: String
    let value: String

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: icon)
                .foregroundStyle(.blue)
                .frame(width: 22)
            Text(title)
                .font(.subheadline.weight(.semibold))
            Spacer()
            Text(value)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }
}

/// Shows a content item's editorial review state. For anything not yet
/// clinically reviewed it adds an explicit caveat so the app never implies that
/// draft material has been approved. SwiftUI color mapping lives here, keeping
/// the model layer Foundation-only.
struct ReviewerStatusBadge: View {
    let status: ReviewerStatus

    private var tint: Color {
        switch status {
        case .draft: return .secondary
        case .needsClinicalReview: return .orange
        case .internallyReviewed: return .blue
        case .externallyReviewed: return .green
        case .institutionSpecific: return .purple
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 10) {
                Image(systemName: status.systemImage)
                    .foregroundStyle(tint)
                    .frame(width: 22)
                Text("Review status")
                    .font(.subheadline.weight(.semibold))
                Spacer()
                Text(status.rawValue)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(tint)
            }

            if !status.isClinicallyReviewed {
                Text(status.explanation)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Review status: \(status.rawValue). \(status.isClinicallyReviewed ? "" : status.explanation)")
    }
}

extension ComplicationRescueCard.Acuity {
    var tintColor: Color {
        switch self {
        case .crash: return .red
        case .urgent: return .orange
        case .watch: return .yellow
        }
    }
}
