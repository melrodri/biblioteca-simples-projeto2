param([switch]$Apresentacao)

# Teste rapido: .\teste-aula3.ps1
# Com pausas para mostrar no navegador: .\teste-aula3.ps1 -Apresentacao
# Se o Learner Lab recriar a API, atualize somente esta URL.
$api = 'https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com'

function Pausar {
    param([string]$Mensagem)
    if ($script:Apresentacao) {
        Write-Host $Mensagem -ForegroundColor Cyan
        Read-Host 'Pressione Enter para continuar' | Out-Null
    }
}

$autorId = $null
$livroId = $null

try {
    Write-Host '1. Consultando os registros atuais...'
    $autores = Invoke-RestMethod -Uri "$api/autores" -Method Get -ErrorAction Stop
    $livros = Invoke-RestMethod -Uri "$api/livros" -Method Get -ErrorAction Stop
    Write-Host "   Autores: $(@($autores).Count); livros: $(@($livros).Count)"

    Write-Host '2. Cadastrando um autor e um livro temporarios...'
    $nome = 'Autor Demo ' + (Get-Date -Format 'HHmmss')
    $autor = Invoke-RestMethod -Uri "$api/autores" -Method Post -ContentType 'application/json' -Body (@{ nome = $nome } | ConvertTo-Json -Compress) -ErrorAction Stop
    $autorId = $autor.id
    $livro = Invoke-RestMethod -Uri "$api/livros" -Method Post -ContentType 'application/json' -Body (@{ titulo = 'Livro Demo'; ano_publicacao = 2020; autor_id = $autorId } | ConvertTo-Json -Compress) -ErrorAction Stop
    $livroId = $livro.id
    Write-Host "   Autor ID $autorId; livro ID $livroId"
    Pausar "   Atualize ${api}/autores e ${api}/livros: os novos registros devem aparecer."

    Write-Host '3. Consultando e editando o livro...'
    $consulta = Invoke-RestMethod -Uri "$api/livros/$livroId" -Method Get -ErrorAction Stop
    $editado = Invoke-RestMethod -Uri "$api/livros/$livroId" -Method Put -ContentType 'application/json' -Body (@{ titulo = 'Livro Demo Editado'; ano_publicacao = 2020; autor_id = $autorId } | ConvertTo-Json -Compress) -ErrorAction Stop
    Write-Host "   Antes: $($consulta.titulo); depois: $($editado.titulo)"
    Pausar "   Atualize ${api}/livros: o titulo deve ser Livro Demo Editado."

    Write-Host '4. Tentando excluir o autor que ainda tem um livro...'
    try {
        Invoke-RestMethod -Uri "$api/autores/$autorId" -Method Delete -ErrorAction Stop | Out-Null
        throw 'Erro: a API permitiu excluir um autor com livro.'
    } catch {
        if (-not $_.Exception.Response -or [int]$_.Exception.Response.StatusCode -ne 409) { throw }
        Write-Host '   HTTP 409: bloqueio correto.'
    }
    Pausar '   O autor continua cadastrado porque ainda possui um livro.'

    Write-Host '5. Excluindo primeiro o livro e depois o autor...'
    Invoke-RestMethod -Uri "$api/livros/$livroId" -Method Delete -ErrorAction Stop | Out-Null
    $livroId = $null
    Invoke-RestMethod -Uri "$api/autores/$autorId" -Method Delete -ErrorAction Stop | Out-Null
    $autorId = $null
    Write-Host '   CRUD concluido. Os registros temporarios foram removidos.'
    Pausar "   Atualize ${api}/autores e ${api}/livros: os registros Demo desapareceram."
} catch {
    Write-Host "Teste interrompido: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "IDs temporarios que podem precisar de limpeza: autor=$autorId livro=$livroId" -ForegroundColor Yellow
    throw
}
