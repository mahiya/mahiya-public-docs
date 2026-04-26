# Elastic Cloud 権限管理ベストプラクティス 参考ドキュメント集

以下は Elastic 公式ドキュメント・ブログから収集した、Elastic Cloud における権限管理の設定に関する参考情報です (関連度の高い順)。

# [Users and roles | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles)
Elastic 環境における認証 (authentication) と認可 (authorization) の全体像を解説するトップページ。Elastic Cloud Hosted / Cloud Serverless / Cloud Enterprise それぞれでの組織レベル、オーケストレーターレベル、クラスタ/デプロイメントレベル、プロジェクトレベルの権限管理モデルの違いを整理している。Cloud Hosted は組織レベルでの SSO とクラスタレベル認証の両方に対応し、Cloud Serverless は組織レベルのロールに集約される。

# [User roles and privileges | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cloud-organization/user-roles)
Elastic Cloud 組織のユーザーに割り当てられるロール (Organization owner / Billing admin / Admin / Editor / Viewer) と、それらを Elastic Stack のロール (superuser / editor / viewer) にマップするデフォルト対応表を提供。組織レベルロールとクラウドリソースアクセスロールの 2 種類を区別し、Serverless プロジェクトの Admin / Developer / Viewer / Editor や SOC manager 等のセキュリティ特化ロールも掲載。

# [Manage users | Elastic Docs (Cloud Organization)](https://www.elastic.co/docs/deploy-manage/users-roles/cloud-organization/manage-users)
Elastic Cloud 組織へのメンバー招待 (UI 操作)、招待時のロール割り当て、および Elastic Cloud API を使った招待・一覧取得・削除の方法。招待リクエスト本文でデプロイメント/プロジェクト単位のロール割り当て (role_id, organization_id, project_ids, application_roles) を指定する例を含む。

# [Manage your Cloud organization | Elastic Docs](https://www.elastic.co/docs/deploy-manage/cloud-organization)
Elastic Cloud 組織 (すべての Elastic Cloud リソース、ユーザー、アカウント設定の最上位単位) 管理のトップページ。ユーザー管理、請求、ID 連携などを行うための入口となるドキュメントで、Elastic が提供する組織管理ツール/API 群へのリンクを含む。

# [Configure Elastic Cloud SAML single sign-on | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cloud-organization/configure-saml-authentication)
SAML 2.0 IdP を使った Elastic Cloud 組織レベル SSO の設定ガイド。ユーザー自動プロビジョニング、SSO 強制、IdP グループから Elastic Cloud ロールへの中央マッピングを提供。組織レベル SSO と デプロイメントレベル SSO の比較表 (プロトコル対応、ロールマッピング範囲、ユーザー体験) と、ロックアウト防止のため最初のロールマッピングに Organization owner を含める推奨事項を掲載。

# [User roles | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/user-roles)
Elastic Stack クラスタ/デプロイメントレベルでの認可の主要手段である RBAC の考え方を説明。RBAC の基本はロールに特権を割り当て、ユーザー/グループにロールを割り当てる。ユーザーの最終権限は複数ロールの和集合となる。属性ベースアクセス制御 (ABAC) にも言及。

# [Defining roles | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/defining-roles)
カスタムロール定義のガイド。Kibana UI、Role Management API、ファイル (`roles.yml`) の 3 通りの管理方法を比較。ファイル方式は各ノードでローカル管理されるため構成管理ツール (Puppet / Chef) で配布を推奨。ECK では Kubernetes Secret を参照して file-based ロールを設定可能。カスタムロールプロバイダプラグイン拡張も可。

# [Role structure | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/role-structure)
カスタムロール定義の JSON 構造の詳細。cluster、indices (names / privileges / field_security / query / allow_restricted_indices)、run_as、metadata、application privileges、リモートインデックス特権 (クロスクラスタ API キーモデル) の構造を、DLS / FLS を含む `clicks_admin` ロールの例と共に解説。

# [Role management using Kibana | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/kibana-role-management)
Kibana UI によるロール管理。`manage_security` クラスタ特権が必要。クラスタ特権・インデックス特権 (Kibana で利用するインデックスには `read` と `view_index_metadata` 推奨)、DLS/FLS、Kibana Spaces ごとの機能特権の設定を解説。同一ロールで異なる Space に異なる特権を割り当てる方法や、複数ロール付与時は特権が和集合になる挙動を説明。

# [Kibana privileges | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/kibana-privileges)
Kibana 特権の基本構造。base 特権 (all / read) と機能別特権 (visualize_v2 / dashboard_v2 など) をロール JSON の spaces 配列とともに設定する例を提示。サブ機能特権によるさらに細かい制御はサブスクリプション機能。

# [Elasticsearch privileges | Elasticsearch Reference](https://www.elastic.co/docs/reference/elasticsearch/security-privileges)
カスタムロール作成時の参考となる、利用可能な cluster / index / application 特権の完全な一覧。`manage_security`、`manage_ml`、`manage_slm`、`cross_cluster_search` など各特権の意味と注意点 (例: 古い datafeed は昇格権限で動作) を網羅。Elastic Cloud Serverless ではインフラ系特権が利用不可な点にも言及。

# [Built-in roles | Elasticsearch Reference](https://www.elastic.co/docs/reference/elasticsearch/roles)
組込みロールのリファレンス。複数ロール付与時は和集合となる。カスタムロールを作る前に `editor` (Kibana 全機能 + データ読み取り)、`reporting_user`、`enrich_user`、`transform_admin/user`、`superuser` (Elastic Cloud でも operator-only 操作は不可) などの組込みロールで要件を満たせないかを検討する指針を提供。

# [Built-in roles | Elasticsearch Guide [8.19]](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/built-in-roles.html)
Elastic Stack が提供する組込みロール (apm_system, beats_admin, kibana_admin, machine_learning_admin/user, monitoring_user, reporting_user, snapshot_user, superuser, transform_admin/user, viewer, watcher_admin など) を網羅。Elastic Cloud では superuser でも operator-only 操作は制限される点を明記。

# [Controlling access at the document and field level | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/controlling-access-at-document-field-level)
データストリーム/インデックスに対して FLS と DLS を組み合わせてアクセス制御する方法。DLS / FLS は読み取り専用特権アカウントで運用するのが前提。ドキュメント制限のロールとフィールド制限のロールを同時に付与すると両方の制限が外れるため、両方を同時に制約したい場合はインデックスを分離すべき点を強調。

# [Quickstart: Native Elasticsearch user and role management | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/quickstart)
Elasticsearch ネイティブレルムを使ったユーザー/ロール管理のクイックスタート。Kibana Spaces でアセットを分離した上で、`acme-marketing-*` 等のインデックスに対し `read` と `view_index_metadata` を付与する `marketing_dashboards_role` の作成例を提示。

# [Create or update roles | Elasticsearch API documentation](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-security-put-role)
`PUT /_security/role/{name}` API の使い方。cluster / indices (名前・特権・field_security・query) / applications / run_as / metadata の構造を持ち、ドキュメントレベルセキュリティを Mustache テンプレートで動的生成する方法も含む。

# [Create or update role mappings API | Elasticsearch Guide [8.19]](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/security-api-put-role-mapping.html)
ロールマッピング API の詳細。ロールを作るのではなく既存ロールにユーザーを紐付ける機能。LDAP DN、realm、ワイルドカードによる複雑なルールに対応し、Mustache テンプレート (`role_templates`) でユーザー属性からロール名を動的生成可能 (例: `_user_<username>`)。`roles` と `role_templates` は同時指定不可。

# [SAML authentication | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/saml)
デプロイメント/クラスタレベル SAML 認証の構成。SAML ユーザーには role mapping API もしくは authorization realm によるロール割り当てが必須 (role mapping ファイルは使用不可)。`principal` / `dn` / `groups` / `metadata` といった SAML 属性マッピングと、realm.name や groups を使ったロールマッピングルールの例を紹介。

# [Manage users and roles (ECE) | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cloud-enterprise-orchestrator/manage-users-roles)
Elastic Cloud Enterprise インストール単位での RBAC 実装手順。admin / readonly / elastic システムユーザーに加えプレビルトロールを利用。セキュリティデプロイメント (3 AZ / 1GB ES ノード推奨) の設定、外部認証プロバイダプロファイルの設定と順序変更、RBAC 有効化後は API アクセスにベアラートークンまたは API キーが必須となる旨を解説。

# [Configure role-based access control | Elastic Cloud Enterprise Reference [3.0]](https://www.elastic.co/guide/en/cloud-enterprise/3.0/ece-configure-rbac.html)
ECE における RBAC 設定のリファレンス。プラットフォーム運用ユーザーに Kibana / Elasticsearch へのログイン権限は付かないこと、セキュリティデプロイメントの構成、プロバイダプロファイルの認証順が権限適用順を左右する点を解説。

# [SAML (ECE) | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cloud-enterprise-orchestrator/saml)
ECE インストールレベルでの SAML SSO 設定手順。SAML 2.0 Web Browser SSO Profile のみサポートのため API クライアント用途には不向き。プロバイダ一般設定、SAML 属性を user property (principal 必須、groups 推奨) にマップし、ロールマッピングで `p_viewer → Platform viewer` のように割り当てる流れを解説。

# [Secure your clusters with SAML | Elastic Cloud Enterprise Reference [3.7]](https://www.elastic.co/guide/en/cloud-enterprise/3.7/ece-securing-clusters-SAML.html)
ECE 管理下 Elasticsearch クラスタを SAML で保護するガイド。saml レルム設定、IdP メタデータアップロード、`attributes.groups` への SAML グループ属性マッピング、`elasticadmins` → `superuser` のようなロールマッピングの例、Kibana 側設定変更 (7.x / 8.x) を記載。

# [Role-based access control and external authentication is GA in ECE 2.3 | Elastic Blog](https://www.elastic.co/blog/rbac-external-authentication-ga-elastic-cloud-enterprise-2-3)
ECE 2.3 で GA となった RBAC と外部認証 (SAML / AD) の概要。Platform admin / Platform viewer 等のプラットフォームロールを紹介し、ECE のロールとホストされるデプロイメント側の資格情報が独立していることを説明。REST API で全操作 (ユーザー CRUD、ロール更新、認証プロバイダ設定) が可能。

# [Role-based access control, and more | Elastic Cloud Release Notes](https://www.elastic.co/guide/en/cloud-hosted/current/ec-release-notes-2023-04-18.html)
Elasticsearch Service (Elastic Cloud Hosted) に RBAC が導入されたリリースノート。組織下のユーザーに標準ロールを割り当て、ロールマッピングをロール別・デプロイメント別に行うことできめ細かな権限管理が可能になった旨を記載。

# [Create an API key | Elasticsearch API documentation](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-security-create-api-key)
`POST/PUT /_security/api_key` API の詳細。expiration、role_descriptors (作成者の権限の部分集合に制限される)、metadata を指定可能。API キー自身で作成された派生キーには特権を指定できない (権限昇格防止) 等、API キー運用上の重要な制約を記述。

# [Authentication | Elasticsearch API documentation](https://www.elastic.co/docs/api/doc/elasticsearch/authentication)
Elasticsearch API が対応する 3 つの認証方式 (Bearer トークン、HTTP Basic、API キー) を解説。`Authorization: ApiKey <encoded>` ヘッダでの呼び出し例、API キーの管理には `/_security/api_key` API を使う旨を提示。

# [User authentication | Elastic Docs](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/user-authentication)
認証有効化時の認証情報付与の基本と、トークンサービス/API キーサービスの役割を説明。API キーサービスは既定で有効、トークンサービスは HTTP の TLS/SSL が有効なときに既定有効。

# [Securing HTTP client applications | Elastic Docs](https://www.elastic.co/docs/deploy-manage/security/httprest-clients-security)
HTTP/REST クライアントからの安全な接続のベストプラクティス。Elasticsearch はステートレスなので各リクエストに資格情報を付与する必要がある。Basic 認証、トークンベース認証、`es-secondary-authorization: ApiKey` ヘッダによるセカンダリ認可の使い方を解説。

# [Get user privileges | Elasticsearch API documentation](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-security-get-user-privileges)
`GET /_security/user/_privileges` API。現在ログインしているユーザーの cluster / indices / applications / run_as 権限を取得する。他ユーザーを確認するには run_as を使用。権限設計の検証用途に有用。

# [Elastic Cloud Information Security Overview (PDF)](https://www.elastic.co/pdf/elastic-cloud-security-guide.pdf)
Elastic Cloud の情報セキュリティに関する公式概要 PDF。社内において最小権限の原則 (Principle of Least Privilege) を適用していること、Elastic 製品が顧客に RBAC によるきめ細かなアクセス管理機能を提供していることを解説。オンボーディング/オフボーディングや IAM プロビジョニング、職責分離といった運用面のベストプラクティスも含む。

# [5 best practices for Elastic Cloud production deployment | Elastic Blog](https://www.elastic.co/blog/5-key-components-optimal-elastic-cloud-production-deployment)
Elastic Cloud を本番導入する際に押さえるべき 5 つのベストプラクティスを解説するブログ。共有責任モデルを前提に、アーキテクチャ設計、ILM によるデータ管理と並び、Kibana ユーザーに対する RBAC、プログラム的アクセスには API キー、SAML / OIDC / Kerberos による SSO をセキュリティ上の推奨事項として挙げている。

# [Secure Elasticsearch with TLS encryption and role-based access control | Elastic Blog](https://www.elastic.co/blog/getting-started-with-elasticsearch-security)
6.8 / 7.1 以降デフォルト配布で無料提供されるセキュリティ機能を使い、2 ノードクラスタの TLS 化、Kibana のセキュリティ有効化、read_logs / read_flight といったインデックス単位のロール作成、ユーザー割り当てまでを一通り体験するチュートリアル。

# [The easy way to find security privileges in Elasticsearch | Elastic Blog](https://www.elastic.co/blog/the-easy-way-to-find-security-privileges-in-elasticsearch)
最小権限の調べ方に関する実践的ブログ。まずは空権限のロールで操作を試し、403 エラーメッセージから必要特権 (例: `view_index_metadata`, `create_doc`, `auto_configure`) を反復的に特定する手順を紹介。`all` 特権は削除権限も含むため強いセキュリティ要件下ではきめ細かい特権を使うべきと指摘。

# [Spaces | Elastic Docs](https://www.elastic.co/docs/deploy-manage/manage-spaces)
Kibana Spaces の仕組みと権限連携。各 Space は独自の saved object を持ち、ロール単位で Space ごとに異なる権限を付与可能。機能の非表示設定はセキュリティではなく UI ヒントに過ぎないため、真のアクセス制御は Kibana Security で構成する必要がある点に注意。

# [Security | Elastic Docs](https://www.elastic.co/docs/deploy-manage/security)
Elastic セキュリティの俯瞰ページ。Kibana の保存オブジェクト (ダッシュボード、可視化、アラート、コネクタ、設定) が機密情報 (PagerDuty キーやメール資格情報など) を含む場合、暗号化キーで暗号化され、キーローテーションも可能。

# [Elastic (ELK) Stack Security](https://www.elastic.co/elastic-stack/security)
Elastic Stack セキュリティ機能の全体概観。AD / LDAP / ネイティブ realm / SAML / Kerberos / カスタム realm 等での認証、RBAC による Kibana Spaces を含むアクセス制御、クラスタ内・クライアント間通信の暗号化を解説するマーケティングページ。

# [Kibana features list | Elastic](https://www.elastic.co/kibana/features)
Kibana のセキュリティ関連機能の一覧。RBAC、Secure Spaces、`kibana_dashboard_only_user` 組込みロール、Native / LDAP / AD / PKI / File / SAML / Kerberos / JWT 等の security realms、SAML SSO、Role Management API を含む。

# [Elasticsearch security: Best practices to keep your data safe | Elastic Videos](https://www.elastic.co/webinars/elasticsearch-security-best-practices-to-keep-your-data-safe)
Elasticsearch のセキュリティ機能を網羅するウェビナー。認証、RBAC、TLS など、デフォルト配布で利用できるセキュリティ機能を紹介し、Elastic Cloud ではこれらが標準で使える点を強調。機密データ保護のための権限設計の考え方を学べる。

# [SAML based Single Sign-On with Elasticsearch and Azure Active Directory | Elastic Blog](https://www.elastic.co/blog/saml-based-single-sign-on-with-elasticsearch-and-azure-active-directory)
Azure AD と Elasticsearch の SAML SSO 構築実例。AAD 側で Enterprise Application を作成し appRoles を SAML Roles クレームとして送信、groups 属性へマップ。SAML 全ユーザーに `kibana_user`、`superuser` app role 保持者に `superuser` を割り当てる 2 つのロールマッピングを作る流れを紹介。

# [Securing GDPR Personal Data with Access Controls | Elastic Blog](https://www.elastic.co/blog/securing-gdpr-personal-data-with-access-controls)
GDPR 対応を題材に、X-Pack セキュリティ機能 (RBAC、document-level security、field-level security、attribute-based access control) を組み合わせて個人データを保護する実践例。ロール数の爆発を防ぐためにユーザーメタデータとテンプレート化クエリによる ABAC を活用するパターンを紹介。

# [Control access to cases | Elastic Docs](https://www.elastic.co/docs/explore-analyze/cases/control-case-access)
Elastic のケース機能へのアクセス制御。Kibana 機能特権で All / Read / None を組み合わせ、ケース管理のフルアクセス、担当者、閲覧のみといったロールを設計。ケース担当者として割り当てるには事前にデプロイメントへ 1 度ログインしてユーザープロファイルを作成する必要がある。

# [Roles and privileges (Fleet) | Elastic Docs](https://www.elastic.co/docs/reference/fleet/fleet-roles-privileges)
Fleet とインテグレーションへのアクセスを Kibana ロール/特権 (all / read / none) で管理する方法を解説。組込みの editor / viewer ロールに加え、Elastic Stack 9.1 以降ではエージェント、エージェントポリシーなどのサブ機能単位で細かく特権を設定可能。用途ごとに異なる利用者に必要最小限の権限を付与する例を示している。

# [Permissions and access control in Elastic Agent Builder | Elastic Docs](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/permissions)
Elastic Agent Builder に対するアクセス制御の 3 層 (Kibana feature、Elasticsearch cluster、Elasticsearch index)。agentBuilder 機能の Read / All に加え Manage agents / Manage tools のサブ機能特権、API キーの Kibana Spaces スコープ (`resources: [space:production]`)、space 単位の URL パスの指定方法を記述。

# [Document level security for content connectors | Elasticsearch Reference](https://www.elastic.co/docs/reference/search-connectors/document-level-security)
8.9.0 以降 Elastic コンテンツコネクタで利用できる DLS (ベータ機能) の概要。ユーザー/グループ権限に応じて検索結果を制限。Workplace Search は独自権限システムを持ち、App Search はこの機能を使わない点に注意。

# [Adding document level security (DLS) to your knowledge search - Elasticsearch Labs](https://www.elastic.co/search-labs/blog/dls-internal-knowledge-search)
DLS の仕組み (ドキュメントにメタデータを埋め込み、クエリフィルタをロールに埋め込む) と、Elastic connector が `_allow_access_control` フィールドや `.search-acl-filter-<index>` インデックスを同期し DLS に必要なロール/API キーを自動構築する仕組みを解説。

# [RAG & RBAC integration: Protect data and boost AI capabilities - Elasticsearch Labs](https://www.elastic.co/search-labs/blog/rag-and-rbac-integration)
RAG アプリケーションに Elasticsearch の RBAC を組み合わせ、例えば「給与情報はマネージャのみが参照可能」といったポリシーを LLM の検索結果に反映させる手法を解説。RBAC レベルと DLS / FLS の使い方、認証済みユーザーに応じたクエリフィルタリングの例を示す。
