import SwiftUI

struct EmptyStateView: View {
    let title: String
    let message: String
    let systemImage: String

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: systemImage)
                // .system(size:) is Dynamic-Type-invariant; .largeTitle scales.
                .font(.largeTitle)
                .foregroundStyle(.secondary)
                .accessibilityHidden(true)
            Text(title)
                .font(.headline)
            Text(message)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding()
        // Only the width is expanded. This view is used both as a full-screen
        // replacement and as a List row; maxHeight: .infinity would stretch
        // the row case.
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .combine)
    }
}
