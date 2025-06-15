// pages/api/ask.ts
export default async function handler(req: any, res:any) {
  const { question } = req.body;

  // Simulasi jawaban
  res.status(200).json({
    answer: `This is a simulated answer for: "${question}"`,
    sources: [
      { content: 'Revenue breakdown is shown in Note 5.', page: 7 },
      { content: 'Net profit appears in consolidated statement.', page: 2 },
    ],
  });
}
