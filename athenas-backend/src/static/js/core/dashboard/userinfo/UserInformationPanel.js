Ext._define('core.dashboard.userinfo.UserInformationPanel', {
    extend: 'Ext.Panel',

    mixins: { '1': 'core.utils.LoadMaskMixin' },

    breakifyEmail: function (email) {
        email = email.replace('@', '@<wbr>');
        email = email.split('.').join('.<wbr>');
        return email;
    },

    normalizePath: function (path) {
        return '/' + global.Context + path;
    },

    getXTemplate: function () {
        if (this._template) {
            return this._template;
        }

        this._template = Ext._create('Ext.XTemplate', [
            '<div class="dashboard-uinfo-container">',
                '<div class="dashboard-uinfo-item dashboard-uinfo-value dashboard-uinfo-photo" ',
                    'onclick="javascript:toolkit.Application.createFormFor(\'RegistrationFormInformation\')">',
                    '<div style="background: url({foto}) no-repeat"></div>',
                    //'<div style="background: url(https://athenas.mpto.mp.br{foto}) no-repeat"></div>',
                '</div>',
                '<tpl if="nome">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Nome:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">{nome}</div>',
                '</tpl>',
                '<tpl if="username">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Usuário:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">{username}</div>',
                '</tpl>',
                '<tpl if="matricula">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Matrícula:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">{matricula}</div>',
                '</tpl>',
                '<tpl if="mail">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">E-mail:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value dashboard-uinfo-email">{mail}</div>',
                '</tpl>',
                '<tpl if="ramais">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Telefones:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">',
                        '<tpl for="ramais">',
                            '<div class="dashboard-uinfo-multivalued">{.}</div>',
                        '</tpl>',
                    '</div>',
                '</tpl>',
                '<tpl if="lotacao">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Lotação:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">',
                        '<tpl for="lotacao">',
                            '<div class="dashboard-uinfo-multivalued">{.}</div>',
                        '</tpl>',
                    '</div>',
                '</tpl>',
                '<tpl if="cargo">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Cargo:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">',
                        '<tpl for="cargo">',
                            '<div class="dashboard-uinfo-multivalued">{.}</div>',
                        '</tpl>',
                    '</div>',
                '</tpl>',
                '<tpl if="funcao">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Função:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">{funcao}</div>',
                '</tpl>',
                '<tpl if="dataReferenciaFerias">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Data base (progressão e férias):</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">{dataReferenciaFerias}</div>',
                '</tpl>',
                '<tpl if="natural">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Natural de:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">{natural}</div>',
                '</tpl>',
                '<tpl if="ecivil">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Estado civil:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">{ecivil}</div>',
                '</tpl>',
                '<tpl if="tsangue">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Sangue:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">{tsangue}</div>',
                '</tpl>',
                '<tpl if="dorgao">',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-label">Doador:</div>',
                    '<div class="dashboard-uinfo-item dashboard-uinfo-value">{dorgao}</div>',
                '</tpl>',
            '</div>',
        ]);

        return this._template;
    },

    getReloadButton: function (cfg) {
        if (this._reloadButton) {
            return this._reloadButton;
        }

        this._reloadButton = Ext._create('Ext.Button', {
            tooltip: 'Recarregar informações',
            icon: this.normalizePath('/static/js/ext/resources/images/default/grid/refresh.gif'),
            scope: this,
            handler: function () {
                this.reloadBody();
            },
        });

        return this._reloadButton;
    },

    getPhoneButton: function (cfg) {
        if (this._phoneButton) {
            return this._phoneButton;
        }

        this._phoneButton = Ext._create('Ext.Button', {
            text: 'Telefone',
            tooltip: 'Atualizar telefone',
            icon: this.normalizePath('/static/images/pda.png'),
            scope: this,
            handler: function () {
                Ext._create('core.dashboard.userinfo.PhoneCRUDWindow', {
                    listeners: {
                        scope: this,
                        destroy: function () {
                            this.reloadBody();
                        },
                    },
                }).show();
            },
        });

        return this._phoneButton;
    },

    getDonorButton: function (cfg) {
        if (this._donorButton) {
            return this._donorButton;
        }

        this._donorButton = Ext._create('Ext.Button', {
            text: 'Doador',
            tooltip: 'Sou doador de orgãos',
            icon: this.normalizePath('/static/images/emblem-favorite.png'),
            scope: this,
            menu: [
                this.getDonorYesMenuItem(cfg),
                this.getDonorNoMenuItem(cfg),
            ],
        });

        return this._donorButton;
    },

    getDonorYesMenuItem: function (cfg) {
        if (this._donorYesMenuItem) {
            return this._donorYesMenuItem;
        }

        this._donorYesMenuItem = Ext._create('Ext.menu.Item', {
            text: 'Sim',
            icon: this.normalizePath('/static/images/accept.png'),
            scope: this,
            handler: function () {
                this.updateDonorInfo({isDonor: 'on'});
            },
        });

        return this._donorYesMenuItem;
    },

    getDonorNoMenuItem: function (cfg) {
        if (this._donorNoMenuItem) {
            return this._donorNoMenuItem;
        }

        this._donorNoMenuItem = Ext._create('Ext.menu.Item', {
            text: 'Não',
            icon: this.normalizePath('/static/images/delete.png'),
            scope: this,
            handler: function () {
                this.updateDonorInfo({isDonor: 'off'});
            },
        });

        return this._donorNoMenuItem;
    },

    getToolbar: function (cfg) {
        if (this._toolbar) {
            return this._toolbar;
        }

        this._toolbar = [
            this.getReloadButton(cfg),
            '-',
            this.getPhoneButton(cfg),
            '-',
            this.getDonorButton(cfg),
        ];

        return this._toolbar;
    },

    updateDonorInfo: function (params) {
        this.showMask();  // mixin

        Ext.Ajax.request({
            url: core.callAction('UserInformation', 'update_donor'),
            method: 'PUT',
            params: params,
            scope: this,
            success: function (response, options) {
                var result = Ext.decode(response.responseText);

                if (!result.success) {
                    Ext.Msg.show({
                        title: 'Atualizando doador',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: result.message,
                    });
                } else {
                    this.reloadBody();
                }
            },
            failure: function (response) {
                Ext.Msg.show({
                    title: 'Atualizando doador',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponível no momento.',
                });
            },
            callback: function () {
                this.hideMask();  // mixin
            },
        });
    },

    fetchUserInformation: function () {
        this.showMask();  // mixin

        Ext.Ajax.request({
            url: core.callAction('UserInformation', 'refresh'),
            method: 'GET',
            scope: this,
            success: function (response, options) {
                var data = Ext.decode(response.responseText);

                if (data.success) {
                    if (data.mail) {
                        data.mail = this.breakifyEmail(data.mail);
                    }
                    this.getXTemplate().overwrite(this.body, data);
                } else {
                    console.error('Informações do usuário:', data.message);
                }
            },
            failure: function (response) {
                Ext.Msg.show({
                    title: 'Informações do usuário',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponível no momento.',
                });
            },
            callback: function () {
                this.hideMask();  // mixin
            },
        });
    },

    getEmptyBody: function () {
        return [
            '<div class="dashboard-emptybody-container">',
                '<span class="dashboard-emptybody-text">',
                    '&lt;',
                    ' Nenhuma informação disponível ',
                    '&gt;',
                '</span>',
            '</div>',
        ].join('');
    },

    reloadBody: function () {
        this.fetchUserInformation();
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            frame: false,
            autoScroll: true,
            html: this.getEmptyBody(),
            tbar: this.getToolbar(cfg),
            listeners: {
                scope: this,
                afterrender: function (panel) {
                    this.reloadBody();
                },
            },
        });

        core.dashboard
          .userinfo
          .UserInformationPanel
          .superclass
          .constructor
          .call(this, cfg);
    },
});
