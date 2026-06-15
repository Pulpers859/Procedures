import SwiftUI

@main
struct ProcedureSTATApp: App {
    @StateObject private var repository = ProcedureRepository()
    @StateObject private var userData = UserDataStore()

    var body: some Scene {
        WindowGroup {
            RootTabView()
                .environmentObject(repository)
                .environmentObject(userData)
        }
    }
}
