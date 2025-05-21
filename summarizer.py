import logging
import time

def summarize_medical_report(report_title, chunks, llm, audience="practitioner"):
    chunk_summaries = []

    def build_chunk_prompt(content):
        if audience == "practitioner":
            return f"""
            You are a medical assistant. Analyze the following section of a medical report titled "{report_title}".

            Extract and summarize relevant clinical information:
            - Chief complaint (if mentioned)
            - Key observations and findings
            - Diagnoses or medical impressions
            - Treatments or procedures
            - Recommendations or next steps

            Text:
            {content}
            """
        else:
            return f"""
            You are explaining part of a medical report titled "{report_title}" to a patient who does not have a medical background.

            Summarize this in simple, clear language. Include:
            - What the main health concern is
            - What the doctor found
            - Any diagnosis or concern
            - What was done or advised
            - What to expect next

            Avoid medical jargon and keep it easy to understand.

            Text:
            {content}
            """

    def build_combined_prompt(summaries):
        if audience == "practitioner":
            return f"""
            You are a clinical summarization expert. Given the following partial summaries of a medical report titled "{report_title}",
            write a clear and comprehensive final summary that combines all key information.

            Use bullet points or organized sections. Be concise but include important clinical details.

            Partial summaries:
            {summaries}
            """
        else:
            return f"""
            You are summarizing a full medical report titled "{report_title}" for a patient or their family.

            Combine the following parts into one summary written in plain, easy-to-understand language. Avoid complex terms.

            Summarize:
            - What the health issue is
            - What doctors found
            - What condition is suspected or diagnosed
            - What actions were taken or planned
            - What happens next

            Partial summaries:
            {summaries}
            """

    for i, chunk in enumerate(chunks):
        prompt = build_chunk_prompt(chunk.page_content)
        max_retries = 3

        for retry_count in range(max_retries):
            try:
                result = llm.invoke(prompt)
                chunk_summaries.append(result)

                delay = 5
                logging.info(f"✅ Chunk {i+1}/{len(chunks)} summarized. Waiting {delay}s before next request.")
                time.sleep(delay)
                break

            except Exception as e:
                if "429" in str(e) and retry_count < max_retries - 1:
                    wait_time = min(20 * (retry_count + 1), 60)
                    logging.warning(f"⚠️ Rate limit hit on chunk {i+1}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"❌ Failed to summarize chunk {i+1}: {e}")
                    chunk_summaries.append(f"[Error summarizing chunk {i+1}]")
                    break

    combined_prompt = build_combined_prompt("\n".join(chunk_summaries))
    try:
        final_result = llm.invoke(combined_prompt)
        return final_result.content if hasattr(final_result, "content") else final_result
    except Exception as e:
        logging.error(f"Error generating final summary: {str(e)}")
        return f"Error generating final summary: {str(e)}"
