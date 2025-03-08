import os
import glob
from correct_pdf import correct_pdf_orientation

def process_directory(input_dir='data', output_dir='data_correct', dpi=200, verbose=False):
    """
    Process all PDF files in the input directory and save corrected versions to output directory

    Args:
        input_dir (str): Input directory containing PDF files
        output_dir (str): Output directory for corrected PDF files
        dpi (int): DPI for PDF conversion
        verbose (bool): Show detailed processing information
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all PDF files in the input directory
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    print(f"Found {len(pdf_files)} PDF files in {input_dir}")

    # Process each PDF file
    for pdf_file in pdf_files:
        filename = os.path.basename(pdf_file)
        output_path = os.path.join(output_dir, filename)

        print(f"\nProcessing: {filename}")
        correct_pdf_orientation(pdf_file, output_path, dpi, verbose)

    print(f"\nAll files processed. Corrected PDFs saved to {output_dir}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Correct orientation of PDF files in a directory')
    parser.add_argument('--input_dir', default='data', help='Input directory containing PDF files')
    parser.add_argument('--output_dir', default='data_correct', help='Output directory for corrected PDF files')
    parser.add_argument('--dpi', type=int, default=200, help='DPI for PDF conversion')
    parser.add_argument('--verbose', action='store_true', help='Show detailed processing information')

    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir, args.dpi, args.verbose)