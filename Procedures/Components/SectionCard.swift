import SwiftUI

struct SectionCard<Content: View>: View {
    let title: String
    var systemImage: String? = nil
    var miniHeight: CGFloat? = nil
    @ViewBuilder let content: Content

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
