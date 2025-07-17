# Research Paper Network

This project provides tools for extracting titles and abstracts from academic papers in PDF format. It utilizes PyMuPDF for PDF processing and NLTK for natural language processing tasks. Additionally, it integrates with an AI model to classify abstracts into relevant Fields of Study (FOS).

## Project Structure

```
ResearchPaperNetwork
├── src
│   ├── extractTitle.py  # Functions to extract and preprocess titles from PDFs
│   ├── extractFOS.py    # Functions to extract abstracts and classify them into FOS
├── main.py              # Entry point for the Streamlit application
├── requirements.txt     # Lists project dependencies
└── README.md            # Documentation for the project
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ResearchPaperNetwork
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit application:
   ```
   streamlit run main.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Upload a PDF document using the provided interface.

4. The application will extract the title and abstract from the PDF and classify the abstract into relevant Fields of Study.

## Dependencies

- Streamlit
- PyMuPDF
- NLTK
- Google Generative AI (for FOS classification)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.