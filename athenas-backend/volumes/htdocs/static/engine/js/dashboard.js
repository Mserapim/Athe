
if(!toolkit.engine.dashboard) {

    toolkit.engine.dashboard = {
        dashPanels: [],
        
        registerDashPanel: function(dashPanelInformation) {
        }
    };

    toolkit.engine.dashboard.DashPanel = Ext.extend(
        Ext.Panel,
        {}
    );

    toolkit.engine.dashboard.EmptyDashPanel = Ext.extend(
        toolkit.engine.dashboard.DashPanel,
        {
            constructor: function() {
                var cf = {
                    border: true,
                    title: 'Bloco Limpo',
                    draggable: true,
                    tools: [
                        {
                            id: 'refresh'
                        },
                        {
                            id: 'gear'
                        },
                        {
                            id: 'close'
                        }
                    ]
                };
                
                toolkit.engine.dashboard.EmptyDashPanel.superclass.constructor.call(this, cf);
            }
        }
    );

    toolkit.engine.dashboard.Dashboard = Ext.extend(
        Ext.Panel,
        {
            getDashPanel: function() {
                if(!this.dashPanel) {
                    this.dashPanel = new Ext.Panel({
                        border: false,
                        style: 'margin: 5px',
                        layout: 'column',
                        items: [
                            {
                                border: false,
                                columnWidth: 0.33,
                                style: 'padding: 5px',
                                height: 200,
                                layout: 'fit',
                                items: new toolkit.engine.dashboard.EmptyDashPanel()
                            },
                            {
                                border: false,
                                columnWidth: 0.34,
                                style: 'padding: 5px',
                                height: 200,
                                layout: 'fit',
                                items: new toolkit.engine.dashboard.EmptyDashPanel()
                            },
                            {
                                border: false,
                                columnWidth: 0.33,
                                style: 'padding: 5px',
                                height: 200,
                                layout: 'fit',
                                items: new toolkit.engine.dashboard.EmptyDashPanel()
                            }
                        ]
                    });
                }

                return this.dashPanel
            },
            
            constructor: function() {
                var cf = {
                    title: 'Não definido',
                    closable: true,
                    items: this.getDashPanel()
                };

                toolkit.engine.dashboard.Dashboard.superclass.constructor.call(this, cf);

                var ts = toolkit.Application.tabspace;
                var ap = ts.getActiveTab();

                ts.remove(ap);
                ts.add(this);
                ts.setActiveTab(this);
            }
        }
    );
}