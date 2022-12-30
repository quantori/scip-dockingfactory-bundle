def buildInDocker(String installPrefix, String platform, String release, String arch){
    script {
        def gitVersion = sh(script: "git describe --always --tags --match=v[0-9]*", returnStdout: true).trim()
        def prefix = sh(script: "echo BUNDLE/${platform}/${release}/\$(uname -m)", returnStdout: true).trim()
        def image = docker.build("build/${prefix}:latest".toLowerCase(), "-f components/scip-bundle/Dockerfile.${platform}${release} ./")
        image.inside("-v ${pwd(tmp: true)}:${installPrefix}") {
            sh("""
               export NPM_CONFIG_CACHE=${installPrefix}/.npm
               git config user.name 'SCIP Jenkins' && git config user.email 'jenkins@scip.lo'
               /build-entrypoint.sh make -j16 bundle BUNDLE_PATH=${installPrefix}/bundle BUNDLE_TARBALL=${installPrefix}/bundle.tgz
               """
            )
        }
        sh("envsubst '\${SCIP_DEPLOYMENT_BUCKET} \${SCIP_OWNER}' < init/pre_install.sh | aws s3 cp - s3://${SCIP_DEPLOYMENT_BUCKET}/bundles/${gitVersion}/pre_install.sh")
        sh("cat init/init_script.sh ${pwd(tmp: true)}/bundle.tgz | aws s3 cp - s3://${SCIP_DEPLOYMENT_BUCKET}/bundles/${gitVersion}/post_install-${platform}${release}_${arch}.sh")
    }
}

pipeline {

    agent none

    environment {
        BUILD_TIME = new Date().format('yyyyMMdd')
        BUNDLE_PATH = '/shared'
    }

    stages {
        stage("Build bundles in parallel") {
            parallel {
                stage('ARM64: Amazon Linux 2') {
                    agent { label 'arm' }

                    steps {
                        buildInDocker(env.BUNDLE_PATH, 'amazon', '2', 'arm')
                        cleanWs()
                    }
                }
                stage('x86_64: Amazon Linux 2') {
                    agent { label 'x86_64&&amazon2' }
                    steps {
                        buildInDocker(env.BUNDLE_PATH, 'amazon', '2', 'x86')
                        cleanWs()
                    }
                }
                stage('x86_64: CentOS 7') {
                    agent { label 'x86_64&&centos7' }
                    steps {
                        buildInDocker(env.BUNDLE_PATH, 'centos', '7', 'x86')
                        cleanWs()
                    }
                }
            }
        }

    }
}

