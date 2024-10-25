FROM python:3.9.17-buster

ARG GITLAB_USER_NAME GITLAB_USER_EMAIL REMOTE_REPOSITORY PAGES_BRANCH CI_COMMIT_BRANCH DOC_VERSION
ENV PAGES_BRANCH=pages

WORKDIR /home/wisenut/app
COPY ./ ./

RUN pip3 install -r ./docs/requirements.txt
RUN git config --global user.name $GITLAB_USER_NAME
RUN git config --global user.email $GITLAB_USER_EMAIL
RUN git remote set-url origin $REMOTE_REPOSITORY
RUN git fetch origin --depth=1
RUN git checkout -b $CI_COMMIT_BRANCH origin/$CI_COMMIT_BRANCH
RUN cd docs && git add .
RUN cd docs && mike deploy --update-aliases ${DOC_VERSION} latest --branch ${PAGES_BRANCH} --deploy-prefix public
RUN cd docs && mike set-default latest --branch ${PAGES_BRANCH} --deploy-prefix public

EXPOSE 8080

CMD cd docs && mike serve --dev-addr 0.0.0.0:8080 --branch $PAGES_BRANCH