import SwiftUI

struct RootTabView: View {
    @AppStorage("ProcedureSTAT.hasAcceptedClinicalDisclaimer") private var hasAcceptedClinicalDisclaimer = false

    var body: some View {
        TabView {
            GuideHomeView()
                .tabItem { Label("Guide", systemImage: "sparkles.rectangle.stack") }

            ProcedureListView()
                .tabItem { Label("Procedures", systemImage: "list.bullet.rectangle") }

            ComplicationsHomeView()
                .tabItem { Label("Rescue", systemImage: "lifepreserver.fill") }

            EquipmentHomeView()
                .tabItem { Label("Kits", systemImage: "checklist.checked") }

            SavedView()
                .tabItem { Label("Saved", systemImage: "bookmark.fill") }
        }
        .tint(.blue)
        .alert("Clinical Review Tool", isPresented: Binding(
            get: { !hasAcceptedClinicalDisclaimer },
            set: { newValue in
                if newValue == false { hasAcceptedClinicalDisclaimer = true }
            }
        )) {
            Button("I Understand", role: .cancel) {
                hasAcceptedClinicalDisclaimer = true
            }
        } message: {
            Text("ProcedureSTAT is for rapid educational review by trained clinicians. It does not replace formal training, supervision, credentialing, clinical judgment, or local institutional policy.")
        }
    }
}
