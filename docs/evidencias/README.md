# Evidências da entrega final

1. [Aplicação na EC2](01-aplicacao.jpeg)
2. [Logs de teste e consulta de capa](02-cloudwatch.jpg)
3. [Sub-redes da VPC](03-sub-redes-vpc.jpg)
4. [RDS sem acesso público](04-rds-privado.jpg)
5. [Capa no S3](05-objeto-s3.jpg)
6. [Processamento automático no CloudWatch](06-cloudwatch-rf03.jpg)
7. [Novo upload no S3](07-s3-upload-rf03.jpg)

No teste final, um upload com URL pré-assinada criou um PNG de 32.693 bytes para o livro 12. O S3 chamou a Lambda automaticamente e a API retornou os dados da nova capa. O teste anterior, mostrado no print 02, usou uma invocação manual.

Veja o [roteiro para repetir o teste](../parte4.md#teste-de-ponta-a-ponta-do-rf-03).
