import SwiftUI

struct ShiftModeHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @State private var searchText = ""

    private var highRiskProcedures: [Procedure] {
        repository.procedures.filter { $0.difficulty == .advanced || $0.difficulty == .rareCrash }
    }

    private var procedures: [Procedure] { repository.search(searchText) }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Text("Open here when you need the 60-second version before walking into the room.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                if searchText.isEmpty && !highRiskProcedures.isEmpty {
                    Section("High-Risk / Crash Procedures") {
                        ForEach(highRiskProcedures) { procedure in
                            NavigationLink(value: procedure) {
                                ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                            }
                        }
                    }
                }

                Section(searchText.isEmpty ? "All Shift Mode Reviews" : "Search Results") {
                    ForEach(procedures) { procedure in
                        NavigationLink(value: procedure) {
                            HStack(alignment: .center, spacing: 12) {
                                Image(systemName: "bolt.fill")
                                    .foregroundStyle(.yellow)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(procedure.title)
                                        .font(.headline)
                                    Text(procedure.sections.shiftMode.prefix(1).joined())
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                        .lineLimit(2)
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Shift Mode")
            .searchable(text: $searchText, prompt: "Search quick review…")
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
        }
    }
}
