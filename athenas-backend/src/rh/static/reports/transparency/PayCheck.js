Ext._define('rh.reports.transparency.PayCheck', {
    extend: 'toolkit.widget.TabPanel',

    getMainPanel: function(cfg) {
        if (!this._mainPanel) {
            var panelWidth = 600;
            var panelLeft = (window.innerWidth / 2) - (panelWidth / 2);
            var panelTop = 15;
            this._mainPanel = Ext._create('Ext.Panel', {
                border: false,
                x: panelLeft,
                y: panelTop,
                width: panelWidth,
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Remuneração de todos os servidores e membros ativos',
                        collapsible: true,
                        layout: 'fit',
                        height: 135,
                        items: [
                            Ext._create('rh.reports.transparency.FormPanel', {
                                reportPath: '/to/mpe/gfp/transparency/Payroll_Genrevent',
                                reportName: 'Remuneração de todos os %s ativos'
                            })
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Verbas indenizatórias e outras remunerações temporárias',
                        collapsible: true,
                        collapsed: true,
                        layout: 'fit',
                        height: 135,
                        items: [
                            Ext._create('rh.reports.transparency.FormPanel', {
                                reportPath: '/to/mpe/gfp/transparency/Payroll_Indemnities_other_compensation',
                                reportName: 'Verbas indenizatórias e outras remunerações temporárias %s'
                            })
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Verbas referentes a exercícios anteriores',
                        collapsible: true,
                        collapsed: true,
                        layout: 'fit',
                        height: 135,
                        items: [
                            Ext._create('rh.reports.transparency.FormPanel', {
                                reportPath: '/to/mpe/gfp/transparency/Payroll_PreviousMonth',
                                reportName: 'Verbas referentes a exercícios anteriores',
                                reportParams: {
                                    category: 'M'
                                },
                                fieldsToHide: ['category']
                            })
                        ]
                    }
                ]
            });
        }
        return this._mainPanel;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {title: 'Transparência - Contracheque'});

        Ext.apply(cfg, {
            layout: 'absolute',
            items: this.getMainPanel(cfg)
        });

        rh.reports.transparency.PayCheck.superclass.constructor.call(this, cfg);
    },
});
