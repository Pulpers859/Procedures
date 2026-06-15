import SwiftUI

struct EquipmentHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @State private var searchText = ""

    private var procedures: [Procedure] { repository.search(searchText) }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Text("Kits are the physical room setup layer: what to ask for, what is commonly missing, and what should be in the room before you start.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                Section("Procedure Kits") {
                    ForEach(procedures) { procedure in
                        NavigationLink {
                            ScrollView {
                                EquipmentChecklistContent(procedure: procedure)
                                    .padding()
                            }
                            .background(Color(.systemGroupedBackground))
                            .navigationTitle(procedure.title)
                            .navigationBarTitleDisplayMode(.inline)
                        } label: {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(procedure.title)
                                    .font(.headline)
                                Text("\(procedure.sections.equipment.count) equipment items")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Kits")
            .searchable(text: $searchText, prompt: "Search kit, catheter, suction…")
        }
    }
}
