###[JBSV-3316] PDF calculando com valor errado

Corrigimos um problema no aplicativo onde o PDF de um pedido apresentava o "valor unitário" e "preço por KG" calculados incorretamente para itens com peso variável.

🔧 **O que foi corrigido:**

O erro estava no cálculo que utilizava o valor total e o peso médio de itens com peso variável. Agora o cálculo está correto e alinhado com a informação exibida na tela de consulta.

✅ **Resultado:**

• PDFs agora mostram valores corretos para todos os tipos de produtos
• Informações consistentes entre tela e PDF
• Maior precisão nos relatórios de pedidos

---