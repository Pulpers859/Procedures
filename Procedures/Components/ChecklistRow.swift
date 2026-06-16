import SwiftUI

struct ChecklistRow: View {
    let text: String
    let isChecked: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(alignment: .top, spacing: 10) {
                Image(systemName: isChecked ? "checkmark.circle.fill" : "circle")
                    .foregroundStyle(isChecked ? .green : .secondary)
                    .font(.title3)
                    .accessibilityHidden(true)
                Text(text)
                    .font(.body)
                    .foregroundStyle(.primary)
                    .strikethrough(isChecked)
                    .fixedSize(horizontal: false, vertical: true)
                Spacer(minLength: 8)
            }
            .contentShape(Rectangle())
            .padding(.vertical, 2)
        }
        .buttonStyle(.plain)
        .sensoryFeedback(.selection, trigger: isChecked)
        .accessibilityLabel(text)
        .accessibilityValue(isChecked ? "Checked" : "Not checked")
        .accessibilityAddTraits(isChecked ? .isSelected : [])
        .accessibilityHint("Toggles this checklist item")
    }
}
