import SwiftUI

enum AppLayout {
    // 8pt corners read flat and dated against current iOS surfaces. These are
    // the single highest-leverage visual change in the app: every card, chip
    // container and media well inherits them.
    static let cardRadius: CGFloat = 14
    static let controlRadius: CGFloat = 12
    static let mediaRadius: CGFloat = 14
    static let iconContainerRadius: CGFloat = 12
    static let cardPadding: CGFloat = 14
    static let sectionSpacing: CGFloat = 12
    static let controlMinHeight: CGFloat = 44
    static let readableContentWidth: CGFloat = 760
}

/// Colors for safety-critical *text*.
///
/// `systemOrange` (~2.2:1) and `systemRed` (~3.4:1) on a light background both
/// fail WCAG AA for the small `.caption`/`.footnote` sizes this app uses, and
/// the strings carrying the most risk — "not clinically reviewed", content
/// load failures, danger-zone warnings, review staleness — were the least
/// legible text on screen in light mode. Icons and fills keep the vivid system
/// color, where the contrast requirement is lower; text uses these darkened
/// variants. Dark mode already passed, so it keeps the system color.
enum AppSemanticColor {
    static let warningText = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark
            ? UIColor.systemOrange
            : UIColor(red: 0.66, green: 0.34, blue: 0.00, alpha: 1)
    })

    static let dangerText = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark
            ? UIColor.systemRed
            : UIColor(red: 0.72, green: 0.09, blue: 0.09, alpha: 1)
    })
}

extension View {
    func detailContentColumn() -> some View {
        frame(maxWidth: AppLayout.readableContentWidth, alignment: .leading)
            .frame(maxWidth: .infinity, alignment: .center)
    }
}

struct SectionCard<Content: View>: View {
    let title: String
    var systemImage: String? = nil
    var miniHeight: CGFloat? = nil
    let content: Content

    init(
        title: String,
        systemImage: String? = nil,
        miniHeight: CGFloat? = nil,
        @ViewBuilder content: () -> Content
    ) {
        self.title = title
        self.systemImage = systemImage
        self.miniHeight = miniHeight
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 8) {
                if let systemImage {
                    Image(systemName: systemImage)
                        .foregroundStyle(.blue)
                        .accessibilityHidden(true)
                }
                Text(title)
                    .font(.headline)
                    .accessibilityHeading(.h2)
                    // accessibilityHeading sets the level but does not add the
                    // trait, so without this these titles never reach
                    // VoiceOver's heading rotor and a detail page can only be
                    // traversed bullet by bullet.
                    .accessibilityAddTraits(.isHeader)
                Spacer()
            }
            content
        }
        .padding(AppLayout.cardPadding)
        .frame(maxWidth: .infinity, minHeight: miniHeight, alignment: .topLeading)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous)
                .stroke(.secondary.opacity(0.12), lineWidth: 1)
        )
    }
}

/// A card whose supporting material should not compete with the bedside path
/// on first render. It starts closed and keeps the full source content local,
/// searchable, and available without changing the underlying clinical text.
struct DisclosureSectionCard<Content: View>: View {
    let title: String
    var systemImage: String? = nil
    var miniHeight: CGFloat? = nil
    let content: Content
    @State private var isExpanded = false

    init(
        title: String,
        systemImage: String? = nil,
        miniHeight: CGFloat? = nil,
        @ViewBuilder content: () -> Content
    ) {
        self.title = title
        self.systemImage = systemImage
        self.miniHeight = miniHeight
        self.content = content()
    }

    var body: some View {
        DisclosureGroup(isExpanded: $isExpanded) {
            content
                .padding(.top, 4)
        } label: {
            HStack(spacing: 8) {
                if let systemImage {
                    Image(systemName: systemImage)
                        .foregroundStyle(.blue)
                        .accessibilityHidden(true)
                }
                Text(title)
                    .font(.headline)
                    .accessibilityHeading(.h2)
                    .accessibilityAddTraits(.isHeader)
                Spacer(minLength: 0)
            }
        }
        .padding(AppLayout.cardPadding)
        .frame(maxWidth: .infinity, minHeight: miniHeight, alignment: .topLeading)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous)
                .stroke(.secondary.opacity(0.12), lineWidth: 1)
        )
        .accessibilityHint(isExpanded ? "Collapse section" : "Expand section")
    }
}

struct BulletListView: View {
    let items: [String]
    var markerTint: Color = .blue

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(Array(items.enumerated()), id: \.offset) { _, item in
                HStack(alignment: .top, spacing: 8) {
                    Text("•")
                        .font(.body.weight(.bold))
                        .foregroundStyle(markerTint)
                        .accessibilityHidden(true)
                    Text(item)
                        .font(.body)
                        .fixedSize(horizontal: false, vertical: true)
                        .textSelection(.enabled)
                }
                .accessibilityElement(children: .combine)
            }
        }
    }
}

/// Troubleshooting is authored as `failure: response` whenever possible.
/// Keeping those two parts visually distinct makes the failure state scannable
/// while preserving the complete response text and its clinical wording.
struct TroubleshootingListView: View {
    let items: [String]

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(Array(items.enumerated()), id: \.offset) { index, item in
                if index > 0 {
                    Divider()
                        .padding(.leading, 28)
                }
                TroubleshootingRow(item: item)
            }
        }
    }
}

private struct TroubleshootingRow: View {
    let item: String

    private var parsed: (failure: String, response: String)? {
        guard let separator = item.firstIndex(of: ":") else { return nil }
        let failure = item[..<separator].trimmingCharacters(in: .whitespacesAndNewlines)
        let response = item[item.index(after: separator)...].trimmingCharacters(in: .whitespacesAndNewlines)
        guard !failure.isEmpty, !response.isEmpty else { return nil }
        return (String(failure), String(response))
    }

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.caption.weight(.bold))
                .foregroundStyle(AppSemanticColor.warningText)
                .frame(width: 18, height: 22, alignment: .top)
                .accessibilityHidden(true)

            VStack(alignment: .leading, spacing: 5) {
                if let parsed {
                    HStack(spacing: 7) {
                        Text("FAIL")
                            .font(.caption2.weight(.heavy))
                            .foregroundStyle(AppSemanticColor.warningText)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 3)
                            .background(AppSemanticColor.warningText.opacity(0.14), in: Capsule())
                        Text(parsed.failure)
                            .font(.subheadline.weight(.semibold))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    Text(parsed.response)
                        .font(.subheadline)
                        .fixedSize(horizontal: false, vertical: true)
                        .textSelection(.enabled)
                } else {
                    Text("GUIDANCE")
                        .font(.caption2.weight(.heavy))
                        .foregroundStyle(AppSemanticColor.warningText)
                    Text(item)
                        .font(.subheadline)
                        .fixedSize(horizontal: false, vertical: true)
                        .textSelection(.enabled)
                }
            }
        }
        .padding(.vertical, 9)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityText)
    }

    private var accessibilityText: String {
        guard let parsed else { return "Troubleshooting guidance. \(item)" }
        return "Failure: \(parsed.failure). Response: \(parsed.response)"
    }
}

struct NumberedListView: View {
    let items: [String]
    var markerTint: Color = .blue

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(Array(items.enumerated()), id: \.offset) { index, item in
                HStack(alignment: .top, spacing: 10) {
                    Text("\(index + 1).")
                        .font(.body.weight(.bold))
                        .foregroundStyle(markerTint)
                        .monospacedDigit()
                        .frame(minWidth: 30, alignment: .leading)
                        .accessibilityHidden(true)
                    Text(item)
                        .font(.body)
                        .fixedSize(horizontal: false, vertical: true)
                        .textSelection(.enabled)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Step \(index + 1). \(item)")
            }
        }
    }
}

struct MetadataRow: View {
    let icon: String
    let title: String
    let value: String

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 10) {
                metadataLabel
                Spacer()
                metadataValue
            }
            VStack(alignment: .leading, spacing: 4) {
                metadataLabel
                metadataValue
                    .padding(.leading, 32)
            }
        }
    }

    private var metadataLabel: some View {
        Label {
            Text(title)
                .font(.subheadline.weight(.semibold))
        } icon: {
            Image(systemName: icon)
                .foregroundStyle(.blue)
                .frame(width: 22)
        }
    }

    private var metadataValue: some View {
        Text(value)
            .font(.subheadline)
            .foregroundStyle(.secondary)
            .fixedSize(horizontal: false, vertical: true)
    }
}

/// Shows a content item's editorial review state. For anything not yet
/// clinically reviewed it adds an explicit caveat so the app never implies that
/// draft material has been approved. SwiftUI color mapping lives here, keeping
/// the model layer Foundation-only.
struct ReviewerStatusBadge: View {
    let status: ReviewerStatus

    private var tint: Color {
        switch status {
        case .draft: return .secondary
        case .needsClinicalReview: return .orange
        case .internallyReviewed: return .blue
        case .externallyReviewed: return .green
        case .institutionSpecific: return .purple
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 10) {
                Image(systemName: status.systemImage)
                    .foregroundStyle(tint)
                    .frame(width: 22)
                Text("Review status")
                    .font(.subheadline.weight(.semibold))
                Spacer()
                Text(status.rawValue)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(tint)
            }

            if !status.isClinicallyReviewed {
                Text(status.explanation)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Review status: \(status.rawValue). \(status.isClinicallyReviewed ? "" : status.explanation)")
    }
}

struct LocalReviewPanel: View {
    let sourceStatus: ReviewerStatus
    /// Provenance of the source content. AI drafts relabel the review-date row
    /// so a machine-stamped date is never presented as a human review date.
    var sourceOrigin: ContentSource = .undeclaredDefault
    let sourceLastReviewed: String
    let sourceVersion: String
    let localReviewRecord: LocalReviewRecord?
    /// Whether the clinically material content moved since this was reviewed.
    /// Purely informational — it never revokes the review.
    var materialState: ReviewContentState? = nil
    let markReviewed: () -> Void
    let markNeedsEdits: () -> Void
    let deferReview: () -> Void
    let clearReview: () -> Void

    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false
    @State private var showProvenance = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            if let localReviewRecord {
                HStack(spacing: 10) {
                    Image(systemName: localReviewRecord.disposition.systemImage)
                        .foregroundStyle(tint(for: localReviewRecord.disposition))
                        .frame(width: 22)
                    Text(localReviewRecord.disposition.rawValue)
                        .font(.subheadline.weight(.semibold))
                    Spacer()
                    Text(localReviewRecord.date)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                materialChangeNotice(for: localReviewRecord)
                reviewActions
                Button("Clear Review State") {
                    clearReview()
                }
                .font(.footnote.weight(.semibold))
                .frame(minHeight: AppLayout.controlMinHeight)
                .contentShape(Rectangle())
            } else {
                Text("Not reviewed in this local workspace.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                reviewActions
            }

            if showSourceGovernance {
                Divider().padding(.vertical, 2)
                if localReviewRecord == nil {
                    provenanceRows
                } else {
                    // Once you have recorded your own review, the four
                    // provenance rows repeat a warning the page header already
                    // shows, directly under your own sign-off — which reads as
                    // the app second-guessing the review you just recorded. It
                    // collapses to one line here. It is never removed: this is
                    // where the app discloses that the text is an unreviewed
                    // draft, and your review of a draft does not stop it being
                    // one.
                    DisclosureGroup(isExpanded: $showProvenance) {
                        provenanceRows.padding(.top, 6)
                    } label: {
                        HStack(spacing: 8) {
                            Image(systemName: sourceStatus.systemImage)
                                .foregroundStyle(sourceStatus.isClinicallyReviewed ? Color.secondary : AppSemanticColor.warningText)
                            Text("Content origin: \(sourceOrigin.shortLabel) · v\(sourceVersion)")
                                .font(.footnote)
                                .foregroundStyle(.secondary)
                            Spacer(minLength: 0)
                        }
                        .frame(minHeight: AppLayout.controlMinHeight)
                        .contentShape(Rectangle())
                    }
                    .tint(.secondary)
                    .accessibilityHint("Shows where this content came from and whether it has had formal clinical review")
                }
            }
        }
    }

    @ViewBuilder
    private var provenanceRows: some View {
        VStack(alignment: .leading, spacing: 10) {
            ReviewerStatusBadge(status: sourceStatus)
            MetadataRow(icon: "sparkles", title: "Content source", value: sourceOrigin.displayLabel)
            MetadataRow(
                icon: "calendar",
                title: sourceOrigin == .aiDraft ? "Draft stamped (not a human review date)" : "Source last reviewed",
                value: sourceLastReviewed
            )
            MetadataRow(icon: "number", title: "Source version", value: sourceVersion)
        }
    }

    private var showSourceGovernance: Bool {
        reviewModeEnabled || !hideGovernanceCopy
    }

    private var reviewActions: some View {
        HStack {
            Button {
                markReviewed()
            } label: {
                // The row sets .footnote, which left this around 32pt — the one
                // control in the app under the 44pt minimum, and the one the
                // whole review workflow exists to reach. Its sibling menu and
                // the clear-review button both already set this.
                Label("Reviewed", systemImage: "checkmark.seal")
                    .frame(minHeight: AppLayout.controlMinHeight)
                    .contentShape(Rectangle())
            }
            .buttonStyle(.borderedProminent)

            Menu {
                Button {
                    markNeedsEdits()
                } label: {
                    Label("Needs Edits", systemImage: "square.and.pencil")
                }
                Button {
                    deferReview()
                } label: {
                    Label("Defer", systemImage: "clock")
                }
            } label: {
                Label("More", systemImage: "ellipsis.circle")
                    .frame(minHeight: AppLayout.controlMinHeight)
                    .contentShape(Rectangle())
            }
            .accessibilityLabel("More review actions")
        }
        .font(.footnote.weight(.semibold))
    }

    /// Your review stands. This never revokes it and never asks you to redo
    /// work — it only mentions it when the clinically material text (steps,
    /// doses, contraindications, complications) moved since you looked, so you
    /// can glance and re-confirm. Editorial churn stays silent on purpose: a
    /// notice that fires on every update is a notice nobody reads.
    @ViewBuilder
    private func materialChangeNotice(for record: LocalReviewRecord) -> some View {
        switch materialState {
        case .materialChanged:
            Label(
                "Still marked reviewed. The steps or doses changed since \(record.date) — worth a glance.",
                systemImage: "arrow.triangle.2.circlepath"
            )
            .font(.caption.weight(.semibold))
            .foregroundStyle(AppSemanticColor.warningText)
            .fixedSize(horizontal: false, vertical: true)
            .frame(maxWidth: .infinity, alignment: .leading)
        case .unchanged, .unknownBaseline, .none:
            EmptyView()
        }
    }

    private func tint(for disposition: LocalReviewDisposition) -> Color {
        switch disposition {
        case .reviewed: return .green
        case .needsEdits: return .orange
        case .deferred: return .secondary
        }
    }
}

extension ComplicationRescueCard.Acuity {
    var tintColor: Color {
        switch self {
        case .crash: return .red
        case .urgent: return .orange
        case .watch: return .yellow
        }
    }
}

struct AcuityBadge: View {
    let acuity: ComplicationRescueCard.Acuity

    var body: some View {
        Label(acuity.rawValue.uppercased(), systemImage: systemImage)
            .font(.caption.weight(.bold))
            .padding(.horizontal, 8)
            .padding(.vertical, 5)
            .foregroundStyle(.primary)
            .background(acuity.tintColor.opacity(0.14), in: Capsule())
            .accessibilityLabel("\(acuity.rawValue) acuity")
    }

    private var systemImage: String {
        switch acuity {
        case .crash: return "bolt.fill"
        case .urgent: return "exclamationmark.triangle.fill"
        case .watch: return "eye.fill"
        }
    }
}
