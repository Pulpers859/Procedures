import SwiftUI

struct VisualGuideContent: View {
    let procedure: Procedure

    private var assets: [ProcedureVisualAsset] {
        procedure.visualAssets ?? []
    }

    var body: some View {
        if assets.isEmpty {
            SectionCard(title: "Visual Guide", systemImage: "photo.on.rectangle.angled") {
                Text("No visual guides for this procedure yet.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        } else {
            VStack(alignment: .leading, spacing: 16) {
                ForEach(assets) { asset in
                    VisualAssetCard(asset: asset)
                }
            }
        }
    }
}

struct VisualAssetCard: View {
    let asset: ProcedureVisualAsset
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false

    private var kindTint: Color {
        switch asset.kind {
        case .landmark: return .blue
        case .probePosition: return .cyan
        case .dangerZone: return .red
        case .confirmation: return .green
        case .setup: return .purple
        }
    }

    private var kindIcon: String {
        switch asset.kind {
        case .landmark: return "mappin.and.ellipse"
        case .probePosition: return "dot.viewfinder"
        case .dangerZone: return "exclamationmark.triangle.fill"
        case .confirmation: return "checkmark.seal.fill"
        case .setup: return "tray.2.fill"
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Kind badge header
            HStack(spacing: 8) {
                Image(systemName: kindIcon)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(kindTint)
                Text(asset.kind.rawValue.uppercased())
                    .font(.caption2.weight(.heavy))
                    .foregroundStyle(kindTint)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.top, 14)
            .padding(.bottom, 10)

            // Image or schematic placeholder
            if let image = ProcedureVisualLoader.image(for: asset) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: .infinity)
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                    .padding(.horizontal, 16)
                    .padding(.bottom, 12)
                    .accessibilityLabel(asset.title)
            } else {
                SchematicPlaceholder(asset: asset, tint: kindTint)
                    .padding(.horizontal, 16)
                    .padding(.bottom, 12)
            }

            // Title + subtitle
            VStack(alignment: .leading, spacing: 4) {
                Text(asset.title)
                    .font(.subheadline.weight(.semibold))
                Text(asset.subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(.horizontal, 16)

            // Clinical warning
            if showGovernanceCopy, let warning = asset.clinicalWarning, !warning.isEmpty {
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundStyle(.orange)
                    Text(warning)
                        .font(.caption)
                        .foregroundStyle(.orange)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
            }

            // Caption
            if !asset.caption.isEmpty {
                Text(asset.caption)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 16)
                    .padding(.top, 6)
            }

            Spacer().frame(height: 14)
        }
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(kindTint.opacity(0.25), lineWidth: 1)
        )
    }

    private var showGovernanceCopy: Bool {
        reviewModeEnabled || !hideGovernanceCopy
    }
}

struct SchematicPlaceholder: View {
    let asset: ProcedureVisualAsset
    let tint: Color

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: asset.systemImage ?? "photo")
                .font(.system(size: 44, weight: .medium))
                .foregroundStyle(tint.opacity(0.7))
                .frame(width: 80, height: 80)
                .background(tint.opacity(0.08), in: RoundedRectangle(cornerRadius: 20, style: .continuous))

            Text("Illustration Pending")
                .font(.caption2.weight(.semibold))
                .foregroundStyle(.secondary)
                .padding(.horizontal, 10)
                .padding(.vertical, 4)
                .background(Color(.tertiarySystemFill), in: Capsule())
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 20)
        .background(tint.opacity(0.04), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
        .accessibilityLabel("\(asset.kind.rawValue) diagram: \(asset.title). Illustration pending.")
    }
}
