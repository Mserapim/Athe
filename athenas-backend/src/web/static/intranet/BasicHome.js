
Ext.ns('web.intranet');

web.intranet.fullAccess = function()
{
    Ext.getCmp('btn-athenas-menu').show();
    Ext.getCmp('btn-athenas-menu').enable();
    // Ext.getCmp('intranet-app').enable();
}

Ext._define('web.intranet.BasicHome', {
	extend: 'toolkit.widget.TabPanel',
    title: 'Intranet básica',
    border: false,
    closable: false,
    layout: {
        type: 'hbox',
        align: 'stretch'
    },

    constructor: function(cfg) {

        // Ext.getCmp('intranet-app').disable();
        Ext.getCmp('btn-athenas-menu').hide();

        web.intranet.BasicHome.superclass.constructor.call(this, {
            items: [
                this._getMenu(),
                this._getNoticePanel(cfg.reason)
            ]
        });
	},

    _getNoticePanel: function(reason)
    {
        if(!this._noticePanel)
        {
            this._noticePanel = Ext._create('Ext.Panel', {
                flex: 1,
                border: false,
                data: {reason: reason},
                tpl: Ext._create('Ext.XTemplate', [
                    '<tpl for=".">',
                        '<div class="intranet-lite">',
                            '<p class="warning">Você está afastado(a).<br/>Motivo, <b>{reason}</b>.<br/>Devido ao afastamento você terá acesso limitado.</p>',
                        '</div>',
                    '</tpl>'
                ])
            });
        }
        return this._noticePanel;
    },

    _getMenu: function()
    {
        if(!this._menuPanel)
        {
            this._menuPanel = Ext._create('Ext.Panel', {
                title: 'Menu',
                region: 'center',
                width: 250,
                data: [
                    {title: 'Comprovantes e requerimentos', href: 'javascript:toolkit.Application.createFormFor(\'GFPReportUsuario\')'},
                    {title: 'Consignações', href: 'javascript:toolkit.Application.createFormFor(\'GFPViabillize\')'}
                ],
                tpl: Ext._create('Ext.XTemplate', [
                    '<div class="intranet intranet-menu">',
                        '<ul>',
                            '<tpl for=".">',
                                '<li><a href="{href}">{title}</a></li>',
                            '</tpl>',
                        '</ul>',
                    '</div>'
                ])
            });
        }
        return this._menuPanel;
    }
});
