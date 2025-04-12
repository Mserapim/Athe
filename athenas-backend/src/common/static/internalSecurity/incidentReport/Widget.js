
Ext._define('common.internalSecurity.incidentReport.Widget', {
    extend: 'engine.notify.NotifyContainer',

    padding: 6,

    actionIconCls: 'icon-isec icon-common-alarm',

    _title: 'Registrar incidente',

    handler: function() {
        var rest = Ext._create('common.internalSecurity.incidentReport.Restful');
        var mask = new Ext.LoadMask(Ext.getBody(), {msg: 'registrando...'});

        mask.show();
        rest.report(
            {
                fn: function(obj) {
                    var notice = new Ext.ToolTip({
                        closable: true,
                        shadow: 'frame',
                        shadowOffset: 7,
                        showDelay: 7000,
                        dismissDelay: 10000,
                        hidden: true,
                        autoHide: true,
                        floating: true,
                        data: {
                            message: obj.message
                        },
                        tpl: new Ext.XTemplate(
                            '<tpl>',
                                '<p id="notice-message" style="cursor:pointer; font-size:15px; font-weight:bold; color:#3366CC; padding:0 0 10px 10px;">',
                                    '{message}',
                                '</p>',
                            '</tpl>'
                        ),
                        listeners: {
                            hide: function()
                            { this.destroy(); }
                        }
                    });

                    notice.showAt([0, 0]);
                    notice.getEl().alignTo(Ext.getBody(), 't-t', [0, 35]);
                },
            },
            {
                fn: function(obj) {}
            },
            {
                fn: function() { mask.hide(); },
            }
        );
    }
});

var rest = Ext._create('common.internalSecurity.incidentReport.Restful');
rest.doRequest(
    rest.getRoute(
      'can_view_panic_button',
      false,
      'GET',
      {
        params: {},
        scope: this,
        success: function(xhr) {
            var rst = Ext.decode(xhr.responseText);
            if (rst.success)
                engine.notify.Manage.register(
                    'incidentReport',
                    'common.internalSecurity.incidentReport.Widget'
                );
        }
    }
));
