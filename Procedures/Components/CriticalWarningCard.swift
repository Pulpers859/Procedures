import SwiftUI

struct CriticalWarningCard: View {
    let title: String
    let items: [String]
    var ordered = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "exclamationmark.triangle.fill")
                    .foregroundStyle(.orange)
                Text(title)
                    .font(.headline)
                    .accessibilityAddTraits(.isHeader)
                Spacer()
            }
            if ordered {
                NumberedListView(items: items, markerTint: .orange)
            } else {
                BulletListView(items: items, markerTint: .orange)
            }
        }
        .padding(AppLayout.cardPadding)
        .background(.orange.opacity(0.12), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous)
                .stroke(.orange.opacity(0.35), lineWidth: 1)
        )
    }
}
