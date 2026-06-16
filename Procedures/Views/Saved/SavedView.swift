import SwiftUI

struct SavedView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore

    private var favorites: [Procedure] {
        repository.procedures.filter { userData.favoriteIDs.contains($0.id) }
    }

    private var recents: [Procedure] {
        userData.recentIDs.compactMap { repository.procedure(withID: $0) }
    }

    private var proceduresWithNotes: [Procedure] {
        repository.procedures.filter { !userData.note(for: $0).trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
    }

    var body: some View {
        NavigationStack {
            List {
                Section("Favorites") {
                    if favorites.isEmpty {
                        Text("Favorite procedures appear here.")
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(favorites) { procedure in
                            NavigationLink(value: procedure) {
                                ProcedureCard(procedure: procedure, isFavorite: true)
                            }
                        }
                    }
                }

                Section("Recently Viewed") {
                    if recents.isEmpty {
                        Text("Recently opened procedures appear here.")
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(recents) { procedure in
                            NavigationLink(value: procedure) {
                                ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                            }
                        }
                    }
                }

                Section("Local Notes") {
                    if proceduresWithNotes.isEmpty {
                        Text("Procedure-specific notes appear here after you add them.")
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(proceduresWithNotes) { procedure in
                            NavigationLink(value: procedure) {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(procedure.title)
                                        .font(.headline)
                                    Text(userData.note(for: procedure))
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                        .lineLimit(2)
                                }
                            }
                        }
                    }
                }

                Section("Content Health") {
                    NavigationLink {
                        ContentHealthView()
                    } label: {
                        HStack {
                            let blockers = repository.contentIssues.filter { $0.severity == .blocker }.count
                            let warnings = repository.contentIssues.filter { $0.severity == .warning }.count
                            let polish = repository.contentIssues.filter { $0.severity == .polish }.count

                            if blockers == 0 && warnings == 0 && polish == 0 {
                                Label("No content issues", systemImage: "checkmark.seal.fill")
                                    .foregroundStyle(.green)
                            } else if blockers > 0 {
                                Label("\(blockers) blockers, \(warnings) warnings", systemImage: "exclamationmark.octagon")
                                    .foregroundStyle(.red)
                            } else if warnings > 0 {
                                Label("\(warnings) warnings, \(polish) polish", systemImage: "exclamationmark.triangle")
                                    .foregroundStyle(.orange)
                            } else {
                                Label("\(polish) polish items", systemImage: "sparkles")
                                    .foregroundStyle(.secondary)
                            }

                            Spacer()
                        }
                        .font(.subheadline)
                    }
                }

                Section("About") {
                    Text(AppConstants.clinicalDisclaimer)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Saved")
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
        }
    }
}
