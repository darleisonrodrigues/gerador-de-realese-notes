import streamlit as st

st.title("🚀 Gerador de Release Notes")
st.write("App funcionando! Agora vamos adicionar as funcionalidades...")

# Teste básico
if st.button("Teste"):
    st.success("Funcionando perfeitamente!")
    
# Mostrar que as variáveis de ambiente funcionam
import os
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    st.success("✅ GROQ_API_KEY configurada!")
else:
    st.warning("⚠️ GROQ_API_KEY não configurada")