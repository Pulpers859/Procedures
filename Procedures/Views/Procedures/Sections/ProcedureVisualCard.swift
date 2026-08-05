import SwiftUI
import UIKit

extension Procedure {
    var hasVisualAssets: Bool {
        guard let assets = visualAssets else { return false }
        return !assets.isEmpty
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
