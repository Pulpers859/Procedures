import SwiftUI

/// Shared "Related Procedures" list, used by both a rescue card's detail
/// screen and a kit's detail screen. Was copy-pasted between the two, which
/// is how one of them silently missed an accessibility fix the other got.
struct RelatedProceduresCard: View {
    let procedures: [Procedure]

    var body: some View {
        if !procedures.isEmpty {
            SectionCard(title: "Related Procedures", systemImage: "link") {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(procedures) { procedure in
                        NavigationLink {
                            ProcedureDetailView(procedure: procedure)
                        } label: {
                            HStack {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(procedure.title)
                                        .font(.subheadline.weight(.semibold))
                                    Text(procedure.category.rawValue)
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(.secondary)
                            }
                            .accessibilityElement(children: .combine)
                            .accessibilityLabel("\(procedure.title), \(procedure.category.rawValue)")
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
    }
}
