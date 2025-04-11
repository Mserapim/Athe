Ext._define('rh.dayoff.activity.DetailWindow', {
    extend: 'Ext.Window',

    width: 560,

    height: 440,

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Detalhes',
                closable: true,
            }
        );
        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'fit',
                items: [
                    this.getFormPanel(cfg)
                ],
                buttons: [
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );


        rh.dayoff.usufruct.ConflictsWindow.superclass.constructor.call(this, cfg);
    },

    getUsufructGrid: function (cfg) {
        if (!this._usufruct)
            this._usufruct = Ext._create('rh.dayoff.usufruct.Grid', {
                region: 'center',
                gridAutoLoad: true,
                split: true,
                frame: false,
                height: 230,
                configOrderToolbar: [],
            });

        this._usufruct.setParam('activity', cfg.activity.pk);
        this._usufruct.setFilterProperty('activity', cfg.activity.pk, 1001);

        return this._usufruct;
    },

    getTemplate: function () {
        var tpl = new Ext.XTemplate(
            '<div class="display-body">',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Servidor:</span>{employee_unicode}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Dias restantes (época oportuna):</span>{days_left_cache}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Autorizado por (chefia imediata):</span>',
            '{immediate_authorization_by_unicode}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Autorizado em (chefia imediata):</span>',
            '{immediate_authorization_at_display}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Autorizado por (chefia mediata):</span>',
            '{mediate_authorization_by_unicode}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Autorizado em (chefia mediata):</span>',
            '{mediate_authorization_at_display}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Autorizado por (Administrador):</span>',
            '{employee_admin_authorization_by}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Autorizado em (Administrador):</span> {admin_authorization_at_display}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Homologado em:</span> {homologation_at_display}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Anexo:</span> {attachment_unicode}&nbsp;',
            '</div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<span style="padding-right: 5px">Justificativa:</span>',
            '</div>',
            '<div style="clear:both"></div>',
            '<div class="display-band" style="padding-bottom: 10px">',
            '<div class="display-text">{justification}</div>',
            '</div>',
            '</div>',
            '<div style="width: 90%; padding-top: 10px;text-align: center;">',
            '<div style="display: inline-block; height: 50px; width: 250px; float: left; width: 60%;">',
            '<div style="font-weight: bold;">Usufrutos marcados</div>',
            '<div>{booked_usufructs_display}</div>',
            '</div>',
            '<div style="display: inline-block; height: 50px; float: left; width: 40%;">',
            '<div style="font-weight: bold;">Usufrutos modificados</div>',
            '<div>{modifieds_usufructs_display}</div>',
            '</div>',
            '</div>'
        );
        return tpl;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {

            var _activity_data = cfg.activity;
            _activity_data.immediate_authorization_at_display = Ext.util.Format.date(cfg.activity.immediate_authorization_at, 'd/m/Y');
            _activity_data.mediate_authorization_at_display = Ext.util.Format.date(cfg.activity.mediate_authorization_at, 'd/m/Y');
            _activity_data.admin_authorization_at_display = Ext.util.Format.date(cfg.activity.admin_authorization_at, 'd/m/Y');
            _activity_data.homologation_at_display = Ext.util.Format.date(cfg.activity.admin_authorization_at, 'd/m/Y');

            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 200,
                html: this.getTemplate().apply(_activity_data),
            });
        }
        return this._formPanel;
    }
});
