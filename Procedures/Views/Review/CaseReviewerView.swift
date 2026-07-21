import SwiftUI

struct CaseReviewerView: View {
    @EnvironmentObject private var userData: UserDataStore
    @AppStorage(SettingsStorageKey.casePrivacyGuardEnabled) private var privacyGuardEnabled = false
    @AppStorage(SettingsStorageKey.caseMentorModel) private var caseMentorModel = CaseMentorDefaults.model

    @State private var title = ""
    @State private var caseText = ""
    @State private var template: CriticalCaseTemplate = .freeform
    @State private var lens: MentorReviewLens = .diagnosticReasoning
    @State private var depth: MentorReviewDepth = .standard
    @State private var isReviewing = false
    @State private var errorMessage: String?
    @State private var latestFeedback: CaseMentorFeedback?
    @State private var deletionTarget: CriticalCaseReview?
    @State private var caseMentorAPIKey = ""

    private var sortedReviews: [CriticalCaseReview] {
        userData.caseReviews.sorted { $0.updatedAt > $1.updatedAt }
    }

    private var privacyFindings: [CasePrivacyFinding] {
        privacyGuardEnabled ? CasePrivacyScanner.findings(in: caseText) : []
    }

    private var canRunReview: Bool {
        !caseText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !isReviewing
    }

    var body: some View {
        List {
            heroSection
            draftSection
            mentorControlsSection
            privacySection
            actionSection
            latestFeedbackSection
            savedReviewsSection
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Case Reviewer")
        .navigationBarTitleDisplayMode(.large)
        .confirmationDialog(
            "Delete this case review?",
            isPresented: Binding(
                get: { deletionTarget != nil },
                set: { if !$0 { deletionTarget = nil } }
            ),
            titleVisibility: .visible
        ) {
            Button("Delete Case", role: .destructive) {
                if let deletionTarget {
                    HapticFeedback.warning()
                    userData.deleteCaseReview(id: deletionTarget.id)
                }
                deletionTarget = nil
            }
        }
        .onChange(of: template) { _, _ in HapticFeedback.selection() }
        .onChange(of: lens) { _, _ in HapticFeedback.selection() }
        .onChange(of: depth) { _, _ in HapticFeedback.selection() }
        .onAppear {
            caseMentorAPIKey = CaseMentorCredentialStore.loadAPIKey()
        }
    }

    private var heroSection: some View {
        Section {
            VStack(alignment: .leading, spacing: 14) {
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: "brain.head.profile")
                        .font(.title2.weight(.semibold))
                        .foregroundStyle(.indigo)
                        .frame(width: 44, height: 44)
                        .background(.indigo.opacity(0.12), in: RoundedRectangle(cornerRadius: 10, style: .continuous))

                    VStack(alignment: .leading, spacing: 5) {
                        Text("AI Mentor Debrief")
                            .font(.title3.weight(.bold))
                        Text("Private case reflection with direct EM and critical-care feedback.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }

                HStack(spacing: 8) {
                    ReviewMetricPill(value: "\(sortedReviews.count)", label: "cases", tint: .indigo)
                    ReviewMetricPill(value: depth.rawValue, label: "depth", tint: depth == .brutal ? .red : .blue)
                    ReviewMetricPill(value: privacyGuardEnabled ? "On" : "Off", label: "privacy", tint: privacyGuardEnabled ? .green : .secondary)
                }
            }
            .padding(.vertical, 4)
        }
    }

    private var draftSection: some View {
        Section {
            TextField("Working title", text: $title)
                .textInputAutocapitalization(.sentences)
                .submitLabel(.done)

            Picker("Template", selection: $template) {
                ForEach(CriticalCaseTemplate.allCases) { option in
                    Label(option.rawValue, systemImage: option.systemImage).tag(option)
                }
            }

            NavigationLink {
                CaseNarrativeEditorView(
                    text: $caseText,
                    privacyGuardEnabled: privacyGuardEnabled,
                    findings: privacyFindings
                )
            } label: {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Case Narrative")
                        .font(.subheadline.weight(.semibold))
                    Text(caseTextPreview)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                .padding(.vertical, 2)
            }
        } header: {
            Text("Case")
        } footer: {
            Text("Use broad, de-identified clinical details. The editor autosaves as you type and supports the normal edge swipe back gesture.")
        }
    }

    private var mentorControlsSection: some View {
        Section {
            Picker("Review Depth", selection: $depth) {
                ForEach(MentorReviewDepth.allCases) { option in
                    Text(option.rawValue).tag(option)
                }
            }
            .pickerStyle(.segmented)

            Picker("Mentor Lens", selection: $lens) {
                ForEach(MentorReviewLens.allCases) { option in
                    Label(option.rawValue, systemImage: option.systemImage).tag(option)
                }
            }
        } header: {
            Text("Mentor")
        }
    }

    @ViewBuilder
    private var privacySection: some View {
        if privacyGuardEnabled {
            Section {
                if privacyFindings.isEmpty {
                    Label("No identifier-like details detected.", systemImage: "checkmark.shield")
                        .foregroundStyle(.green)
                } else {
                    ForEach(privacyFindings) { finding in
                        VStack(alignment: .leading, spacing: 3) {
                            Text(finding.kind.rawValue)
                                .font(.subheadline.weight(.semibold))
                            Text(finding.suggestion)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        .padding(.vertical, 2)
                    }
                }
            } header: {
                Text("Privacy Guard")
            }
        }
    }

    private var actionSection: some View {
        Section {
            Button {
                runMentorReview()
            } label: {
                HStack {
                    Label(isReviewing ? "Reviewing Case" : "Run Mentor Review", systemImage: "sparkles")
                    Spacer()
                    if isReviewing {
                        ProgressView()
                    }
                }
            }
            .disabled(!canRunReview)

            if caseMentorAPIKey.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                Text("Add an OpenAI API key in Settings to run the AI mentor.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            if let errorMessage {
                Text(errorMessage)
                    .font(.caption)
                    .foregroundStyle(.red)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    @ViewBuilder
    private var latestFeedbackSection: some View {
        if let latestFeedback {
            Section("Latest Mentor Review") {
                MentorFeedbackText(feedback: latestFeedback)
            }
        }
    }

    @ViewBuilder
    private var savedReviewsSection: some View {
        Section("Saved Case Reviews") {
            if sortedReviews.isEmpty {
                EmptyStateView(
                    title: "No reviewed cases yet",
                    message: "Write a de-identified case narrative and run a mentor review.",
                    systemImage: "doc.text.magnifyingglass"
                )
            } else {
                ForEach(sortedReviews) { review in
                    NavigationLink {
                        CaseReviewDetailView(review: review)
                    } label: {
                        CaseReviewRow(review: review)
                    }
                    .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                        Button(role: .destructive) {
                            deletionTarget = review
                        } label: {
                            Label("Delete", systemImage: "trash")
                        }
                    }
                }
            }
        }
    }

    private var caseTextPreview: String {
        let trimmed = caseText.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? "Add de-identified details, decision points, reassessments, and disposition." : trimmed
    }

    private func runMentorReview() {
        HapticFeedback.lightTap()
        errorMessage = nil
        isReviewing = true

        let review = CriticalCaseReview(
            title: title,
            template: template,
            lens: lens,
            depth: depth,
            caseText: caseText
        )
        let findings = privacyFindings
        let service = OpenAIResponsesMentorService()
        let apiKey = caseMentorAPIKey
        let model = caseMentorModel

        Task {
            do {
                let feedback = try await service.review(
                    caseReview: review,
                    privacyFindings: findings,
                    apiKey: apiKey,
                    model: model
                )
                var savedReview = review
                savedReview.mentorFeedback = feedback
                savedReview.updatedAt = Date()

                await MainActor.run {
                    userData.saveCaseReview(savedReview)
                    latestFeedback = feedback
                    isReviewing = false
                    HapticFeedback.success()
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isReviewing = false
                    HapticFeedback.warning()
                }
            }
        }
    }
}

private struct CaseNarrativeEditorView: View {
    @Binding var text: String
    let privacyGuardEnabled: Bool
    let findings: [CasePrivacyFinding]

    @Environment(\.dismiss) private var dismiss
    @FocusState private var editorFocused: Bool

    var body: some View {
        ZStack(alignment: .topLeading) {
            TextEditor(text: $text)
                .focused($editorFocused)
                .font(.body)
                .padding(.horizontal, 12)
                .padding(.vertical, 10)
                .scrollDismissesKeyboard(.interactively)

            if text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                Text("Initial frame, vitals, differential, interventions, turning points, reassessments, consults, disposition, and what bothered you afterward.")
                    .font(.body)
                    .foregroundStyle(.tertiary)
                    .padding(.horizontal, 18)
                    .padding(.vertical, 18)
                    .allowsHitTesting(false)
            }
        }
        .safeAreaInset(edge: .bottom) {
            if privacyGuardEnabled && !findings.isEmpty {
                HStack(spacing: 10) {
                    Image(systemName: "checkmark.shield")
                        .foregroundStyle(.orange)
                    Text("\(findings.count) identifier-like detail\(findings.count == 1 ? "" : "s") detected")
                        .font(.footnote.weight(.semibold))
                    Spacer()
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(.bar)
            }
        }
        .navigationTitle("Case Narrative")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button("Done") {
                    HapticFeedback.lightTap()
                    dismiss()
                }
            }
        }
        .onAppear {
            editorFocused = true
        }
    }
}

private struct CaseReviewRow: View {
    let review: CriticalCaseReview

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: review.template.systemImage)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.indigo)
                .frame(width: 32, height: 32)
                .background(.indigo.opacity(0.12), in: RoundedRectangle(cornerRadius: 8, style: .continuous))

            VStack(alignment: .leading, spacing: 3) {
                Text(review.displayTitle)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.primary)
                Text("\(review.template.rawValue) / \(review.lens.rawValue)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                Text(review.updatedAt.formatted(date: .abbreviated, time: .omitted))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }

            Spacer(minLength: 8)

            Text(review.depth.rawValue)
                .font(.caption2.weight(.bold))
                .foregroundStyle(review.depth == .brutal ? .red : .blue)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background((review.depth == .brutal ? Color.red : Color.blue).opacity(0.12), in: Capsule())
        }
        .padding(.vertical, 4)
    }
}

private struct CaseReviewDetailView: View {
    let review: CriticalCaseReview

    var body: some View {
        List {
            Section {
                MetadataRow(icon: "calendar", title: "Reviewed", value: review.updatedAt.formatted(date: .abbreviated, time: .shortened))
                MetadataRow(icon: "doc.text", title: "Template", value: review.template.rawValue)
                MetadataRow(icon: review.lens.systemImage, title: "Mentor Lens", value: review.lens.rawValue)
                MetadataRow(icon: "slider.horizontal.3", title: "Depth", value: review.depth.rawValue)
            }

            Section("Case Narrative") {
                Text(review.caseText)
                    .font(.body)
                    .textSelection(.enabled)
                    .fixedSize(horizontal: false, vertical: true)
            }

            if let feedback = review.mentorFeedback {
                Section("Mentor Review") {
                    MentorFeedbackText(feedback: feedback)
                }
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle(review.displayTitle)
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct MentorFeedbackText: View {
    let feedback: CaseMentorFeedback

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(feedback.content)
                .font(.body)
                .textSelection(.enabled)
                .fixedSize(horizontal: false, vertical: true)

            Divider()

            MetadataRow(icon: "sparkles", title: "Model", value: feedback.model)
            MetadataRow(icon: "clock", title: "Generated", value: feedback.createdAt.formatted(date: .abbreviated, time: .shortened))
        }
        .padding(.vertical, 4)
    }
}
