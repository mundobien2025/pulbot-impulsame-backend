# 0.2.0 (2025-08-16)


### Bug Fixes

* agregar función prepare_user_data faltante ([737c42e](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/737c42ea5cf1f7a1222ec1a213a5d19284dd19e2))
* aumentar timeout y permisos S3 para registro de usuarios ([85c3f20](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/85c3f2042a973effeb8351bae0d08ef867d6ca68))
* **ci:** add automatic cleanup for rollback-complete cloudformation stacks ([36228e6](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/36228e62e9bf0f45a6522f275811c8d96413b3bc))
* **iam:** correct S3 bucket ARN reference in Lambda execution role policy ([3ccfbd8](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/3ccfbd8453ca699a49564043f9b6d10fdccf8f42))
* **lambda:** improve error handling and CORS support for testing ([5fc71fe](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/5fc71fe19dda026fdb6c14d3e6ba5ac4da406345))


### Features

* agregar script generador de usuarios de prueba ([d3e1dea](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/d3e1dea17fa80669917f6e7a49b5ee21967ca9ff))
* **ci:** add automatic changelog generation and semantic versioning ([9810fe8](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/9810fe895d3b9b554b45b76b496c3177f80a08ea))
* implementar funcionalidad completa de registro de usuarios ([58bbe0d](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/58bbe0ddb75617600f287ba25ce6eb2c0e5f4628))
* **runtime:** upgrade lambda runtime to python 3.13 ([b2c5275](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/b2c5275793d088d4e7a12a91d342be906af915ac))
* **s3:** configure bucket as static website with custom domain name and auto-deploy index.html ([e1a89b1](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/e1a89b1922c4f5835c6559f960f62f521cc55c24))
* **s3:** configure bucket for CloudFront integration with custom domain naming ([6c52090](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/6c520902f110fa0a181ef29915e77297b02d0966))
* simplificar registro de usuarios solo con campos de texto ([82246d2](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/82246d22ef0e47a85b85de2facc839a409d96cf9))
* **vpc:** configure lambda functions to run in existing VPC with environment variables ([a9dbdf3](https://github.com/mundobien2025/pulbot-impulsame-backend/commit/a9dbdf3f39bce61750a44e61bbc5bfa982e32a44))



