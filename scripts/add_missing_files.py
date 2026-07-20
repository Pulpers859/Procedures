from pbxproj import XcodeProject
import glob
import os

project_path = r'C:\Dev\Procedures\Procedures.xcodeproj\project.pbxproj'
project = XcodeProject.load(project_path)

# Add all Swift files in the Sections folder
sections_dir = r'C:\Dev\Procedures\Procedures\Views\Procedures\Sections'
swift_files = glob.glob(os.path.join(sections_dir, '*.swift'))

# Also add ProcedureVisualCard if it's somewhere else
visual_card = r'C:\Dev\Procedures\Procedures\Views\Procedures\ProcedureVisualCard.swift'
if os.path.exists(visual_card):
    swift_files.append(visual_card)

added_count = 0
for file_path in swift_files:
    # Check if file is already in project to avoid duplicates
    results = project.get_files_by_path(file_path)
    if not results:
        # We need to provide the target name or just add it to all targets
        # Assuming the main target is Procedures
        project.add_file(file_path, target_name='Procedures', force=False)
        added_count += 1
        print(f"Added {file_path}")

project.save()
print(f"Total files added to pbxproj: {added_count}")
