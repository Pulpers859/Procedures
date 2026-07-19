import SwiftUI
import UIKit

// MARK: - Header visual (only shows when a real image is bundled)

extension Procedure {
    var bundledVisual: (asset: ProcedureVisualAsset, image: UIImage)? {
        guard let asset = primaryVisualAsset,
              let image = ProcedureVisualLoader.image(for: asset) else {
            return nil
        }
        return (asset, image)
    }

    var hasVisualAssets: Bool {
        guard let assets = visualAssets else { return false }
        return !assets.isEmpty
    }
}

struct ProcedureVisualCard: View {
    let asset: ProcedureVisualAsset
    let image: UIImage

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Image(uiImage: image)
                .resizable()
                .scaledToFit()
                .frame(maxWidth: .infinity)
                .clipShape(RoundedRectangle(cornerRadius: AppLayout.mediaRadius, style: .continuous))
                .accessibilityLabel(asset.title)

            Text(asset.title)
                .font(.subheadline.weight(.semibold))

            if let warning = asset.clinicalWarning, !warning.isEmpty {
                Label(warning, systemImage: "exclamationmark.triangle.fill")
                    .font(.caption)
                    .foregroundStyle(.orange)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(AppLayout.cardPadding)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous)
                .stroke(.secondary.opacity(0.12), lineWidth: 1)
        )
    }
}

enum ProcedureVisualLoader {
    static func image(for asset: ProcedureVisualAsset) -> UIImage? {
        guard let assetName = asset.assetName, !assetName.isEmpty else { return nil }

        for name in [assetName, "Visuals/\(assetName)"] {
            if let image = UIImage(named: name) {
                return image
            }
        }

        let name = (assetName as NSString).deletingPathExtension
        let ext = (assetName as NSString).pathExtension
        let extensions = ext.isEmpty ? [nil, "png", "jpg", "jpeg"] : [ext]
        let subdirectories: [String?] = [nil, "Visuals"]

        for subdirectory in subdirectories {
            for itemExtension in extensions {
                if let url = Bundle.main.url(forResource: ext.isEmpty ? assetName : name, withExtension: itemExtension, subdirectory: subdirectory),
                   let image = UIImage(contentsOfFile: url.path) {
                    return image
                }
            }
        }

        return nil
    }
}
