import SwiftUI

struct ProcedureCard: View {
    let procedure: Procedure
    let isFavorite: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .top, spacing: 10) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(procedure.title)
                        .font(.headline)
                        .foregroundStyle(.primary)
                    Text(procedure.category.rawValue)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                VStack(alignment: .trailing, spacing: 6) {
                    if isFavorite {
                        Image(systemName: "bookmark.fill")
                            .foregroundStyle(.blue)
                            .accessibilityLabel("Favorite")
                    }
                    if procedure.difficulty == .advanced || procedure.difficulty == .rareCrash {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundStyle(.orange)
                            .accessibilityLabel("High risk")
                    }
                }
            }

            FlowTagView(tags: [procedure.difficulty.rawValue, procedure.reviewTime] + procedure.setting.map(\.rawValue))
        }
        .padding(.vertical, 8)
    }
}

struct TagView: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.caption.weight(.semibold))
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(.thinMaterial, in: Capsule())
            .foregroundStyle(.secondary)
            .lineLimit(1)
    }
}

struct FlowTagView: View {
    let tags: [String]

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 8) {
                ForEach(tags, id: \.self) { TagView(text: $0) }
            }
            VStack(alignment: .leading, spacing: 6) {
                ForEach(tags, id: \.self) { TagView(text: $0) }
            }
        }
    }
}
