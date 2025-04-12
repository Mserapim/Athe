Ext._define('core.dashboard.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getAbsentNoticeTemplate: function () {
        if (this._absentNoticeTemplate) {
            return this._absentNoticeTemplate;
        }

        this._absentNoticeTemplate = Ext._create('Ext.XTemplate', [
            '<tpl for=".">',
                '<div class="intranet-lite">',
                    '<p class="warning">',
                        '{name}, você está afastado(a).<br/>Motivo, <b>{absentReason}</b>.<br/>',
                        'Devido ao afastamento você terá acesso limitado.',
                    '</p>',
                '</div>',
            '</tpl>'
        ]);

        return this._absentNoticeTemplate;
    },

    showEmployeePortalPanel: function (cfg) {
        var employeePortal = this.getMainContainer().getEmployeePortalContainer();
        !employeePortal.isVisible() && employeePortal.show();
    },

    showAbsentNotice: function (cfg) {
        Ext._create('Ext.Window', {
            title: 'AVISO',
            modal: true,
            frame: true,
            resizable: false,
            maxHeight: 450,
            minWidth: 350,
            maxWidth: 660,
            data: cfg.user.employee,
            tpl: this.getAbsentNoticeTemplate(),
        }).show();
    },

    hideApplicationMenu: function (cfg) {
        toolkit.Application.getMenuPanel().hide();
    },

    checkEmployee: function (cfg) {
        if (!(cfg.user && cfg.user.employee)) {
            console.error('Erro ao verificar informações do usuário/servidor.');
            return;
        }

        if (!(cfg.user.employee.isAbsent || cfg.user.employee.isRetired)) {
            return;
        }

        this.hideApplicationMenu(cfg);
        this.showEmployeePortalPanel(cfg);

        if (cfg.user.employee.isAbsent) {
            this.showAbsentNotice(cfg);
        }
    },

    _closeEvent: function (panel) {
        toolkit.Application.createFormFor('Dashboard');
    },

    getMainContainer: function (cfg) {
        if (this._mainContainer) {
            return this._mainContainer;
        }

        this._mainContainer = Ext._create('core.dashboard.Container');

        return this._mainContainer;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        this.checkEmployee(cfg);

        Ext.applyIf(cfg, {
            title: 'Inicial',
        });

        Ext.apply(cfg, {
            id: 'cmp-dashboard-app',
            layout: 'fit',
            items: this.getMainContainer(cfg),
            listeners: {
                scope: this,
                close: this._closeEvent,
            },
        });

        core.dashboard.Manager.superclass.constructor.call(this, cfg);
    },
});
