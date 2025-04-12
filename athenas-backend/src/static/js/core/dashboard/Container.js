Ext._define('core.dashboard.Container', {
    extend: 'Ext.Container',

    BACKGROUND_COLOR: '#005a7d',

    GAP: 7,  // gap between panels

    getEmployeePortalPanel: function (cfg) {
        if (this._employeePortalPanel) {
            return this._employeePortalPanel;
        }

        this._employeePortalPanel = Ext._create('Ext.Panel', {
            title: 'Portal do servidor',
            baseCls: 'x-river-panel',
            flex: 1,
            layout: 'fit',
            padding: 0,
            items: Ext._create('core.dashboard.EmployeePortalPanel'),
        });

        return this._employeePortalPanel;
    },

    // _TODO_ Reescrever o código que obtém os Manuais
    getManualPanel: function (cfg) {
        if (this._manualPanel) {
            return this._manualPanel;
        }

        var news = Ext._create('toolkit.web.intranet.News');

        this._manualPanel = Ext._create('Ext.Panel', {
            title: 'Manuais',
            baseCls: 'x-river-panel',
            flex: .30,
            margins: `${this.GAP} 0 0 0`,
            autoScroll: true,
            items: [news],
            bbar: [news.getPaging()],
            listeners: {
                scope: this,
                afterrender: function(panel) {
                    news.getStoreAreas(function(storeAreas) {
                        var store = news.getStore();
                        store.setBaseParam('areas__slug__in', '[\'manuais\']');
                    });
                }
            },
        });

        return this._manualPanel;
    },

    getNotificationPanel: function (cfg) {
        if (this._notificationPanel) {
            return this._notificationPanel;
        }

        var notificationPanel = Ext._create('core.dashboard.notification.Panel');

        this._notificationPanel = Ext._create('Ext.Panel', {
            title: 'Notificações',
            baseCls: 'x-river-panel',
            flex: .30,
            margins: `${this.GAP} 0 0 0`,
            layout: 'fit',
            padding: 0,
            items: notificationPanel,
        });

        // Mostra quantidade de notificações não lidas
        notificationPanel.getListView().getStore().on({
            scope: this,
            load: function (store, records, options) {
                var title = 'Notificações';
                var totalUnread = notificationPanel.getListView().getTotalUnread();

                if (totalUnread > 0) {
                    title = `${title} (${totalUnread} não ${totalUnread > 1 ? 'lidas' : 'lida'})`;
                }

                this._notificationPanel.setTitle(title);
            },
        });

        return this._notificationPanel;
    },

    getPendentWorkGrid: function (cfg) {
        if (this._pendentWorkGrid) {
            return this._pendentWorkGrid;
        }

        this._pendentWorkGrid = Ext._create('core.dashboard.PendentWorkGrid');

        // Simula clique sobre o botão/menu "Relatórios" (Tarefas sob demanda)
        this._pendentWorkGrid.on({
            scope: this,
            dblclick: function (event) {
                var selected = this._pendentWorkGrid.getSelectionModel().getSelected();

                if (selected && selected.get('keyId') === 'get_tasks_on_demand_count') {
                    document.getElementById('cmp-tasks-on-demand-menu').click();
                }
            },
        });

        return this._pendentWorkGrid;
    },

    getPendentWorkPanel: function (cfg) {
        if (this._pendentWorkPanel) {
            return this._pendentWorkPanel;
        }

        this._pendentWorkPanel = Ext._create('Ext.Panel', {
            title: 'Trabalhos pendentes',
            baseCls: 'x-river-panel',
            flex: .70,
            layout: 'fit',
            padding: 0,
            items: this.getPendentWorkGrid(cfg),
        });

        return this._pendentWorkPanel;
    },

    getPayCheckPanel: function (cfg) {
        if (this._paycheckPanel) {
            return this._paycheckPanel;
        }

        this._paycheckPanel = Ext._create('Ext.Panel', {
            title: 'Contracheque/Holerite',
            baseCls: 'x-river-panel',
            flex: .5,
            margins: `0 ${this.GAP} ${this.GAP} 0`,
            padding: this.GAP,
            autoScroll: true,
            items: Ext._create('rh.gfp.reports.employee.forms.PayCheckMPMT'),
        });

        return this._paycheckPanel;
    },

    getPointSheetPanel: function (cfg) {
        if (this._pointSheetPanel) {
            return this._pointSheetPanel;
        }

        this._pointSheetPanel = Ext._create('Ext.Panel', {
            title: 'Folha Ponto',
            baseCls: 'x-river-panel',
            flex: .5,
            margins: `0 ${this.GAP} ${this.GAP} 0`,
            padding: this.GAP,
            autoScroll: true,
            items: Ext._create('rh.pvf.reports.PointSheet'),
        });

        return this._pointSheetPanel;
    },

    getFinancialStatementPanel: function (cfg) {
        if (this._financialStatementPanel) {
            return this._financialStatementPanel;
        }

        this._financialStatementPanel = Ext._create('Ext.Panel', {
            title: 'Ficha financeira',
            baseCls: 'x-river-panel',
            flex: .5,
            margins: `0 ${this.GAP} ${this.GAP} 0`,
            padding: this.GAP,
            autoScroll: true,
            items: Ext._create('rh.gfp.reports.employee.forms.FinancialStatement'),
        });

        return this._financialStatementPanel;
    },


    getCalendarPanel: function (cfg) {
        if (this._calendarPanel) {
            return this._calendarPanel;
        }

        this._calendarPanel = Ext._create('Ext.Panel', {
            title: 'Agenda',
            baseCls: 'x-river-panel',
            flex: .5,
            margins: `0 ${this.GAP} ${this.GAP} 0`,
            padding: this.GAP,
            autoScroll: true,
            items: Ext._create('rh.pvf.reports.CalendarForm'),
        });

        return this._calendarPanel;
    },

    getCedulaCPanel: function (cfg) {
        if (this._cedulaCPanel) {
            return this._cedulaCPanel;
        }

        this._cedulaCPanel = Ext._create('Ext.Panel', {
            title: 'Informe de Rendimentos',
            baseCls: 'x-river-panel',
            flex: .5,
            margins: `0 ${this.GAP} ${this.GAP} 0`,
            padding: this.GAP,
            autoScroll: true,
            items: Ext._create('rh.gfp.reports.CedulaCReport'),
        });

        return this._cedulaCPanel;
    },

    getRegisterPointPanel: function (cfg) {
        if (this._registerPointPanel) {
            return this._registerPointPanel;
        }

        this._registerPointPanel = Ext._create('Ext.Panel', {
            title: 'Registrar Ponto',
            baseCls: 'x-river-panel',
            flex: .5,
            margins: `0 0 ${this.GAP} 0`,
            padding: this.GAP,
            autoScroll: true,
            items: Ext._create('rh.registerpoint.RegisterPointForm'),
        });

        return this._registerPointPanel;
    },

    getEmployeeRecordPanel: function (cfg) {
        if (this._employeeRecordPanel) {
            return this._employeeRecordPanel;
        }

        this._employeeRecordPanel = Ext._create('Ext.Panel', {
            title: 'Ficha funcional',
            baseCls: 'x-river-panel',
            flex: .5,
            margins: `0 ${this.GAP} 0 0`,
            padding: this.GAP,
            autoScroll: true,
            items: Ext._create('rh.gfp.reports.employee.forms.EmployeeRecord'),
        });

        return this._employeeRecordPanel;
    },

    getComprovanteRendimentosPanel: function (cfg) {
        if (this._comprovanteRendimentosPanel) {
            return this._comprovanteRendimentosPanel;
        }

        this._comprovanteRendimentosPanel = Ext._create('Ext.Panel', {
            title: 'Comprovante de rendimentos',
            baseCls: 'x-river-panel',
            flex: .5,
            padding: this.GAP,
            autoScroll: true,
            items: Ext._create('rh.gfp.reports.employee.forms.ComprovanteRendimentos'),
        });

        return this._comprovanteRendimentosPanel;
    },

    getUserInfoPanel: function (cfg) {
        if (this._userInfoPanel) {
            return this._userInfoPanel;
        }

        this._userInfoPanel = Ext._create('Ext.Panel', {
            title: 'Informações do usuário',
            baseCls: 'x-river-panel',
            flex: 1,
            layout: 'fit',
            padding: 0,
            items: Ext._create('core.dashboard.userinfo.UserInformationPanel'),
        });

        return this._userInfoPanel;
    },

    getReportContainer: function (cfg) {
        if (this._reportContainer) {
            return this._reportContainer;
        }

        this._reportContainer = Ext._create('Ext.Container', {
            flex: .70,
            layout: {
                type: 'vbox',
                align: 'stretch',
            },
            items: [
                // {
                //     xtype: 'container',
                //     flex: .5,
                //     layout: {
                //         type: 'hbox',
                //         align: 'stretch',
                //     },
                //     items: [
                //         this.getPayCheckPanel(cfg),
                //         this.getFinancialStatementPanel(cfg),
                //         this.getPointSheetPanel(cfg),
                //     ],
                // },
                // {
                //     xtype: 'container',
                //     flex: .5,
                //     layout: {
                //         type: 'hbox',
                //         align: 'stretch',
                //     },
                //     items: [
                //         // this.getEmployeeRecordPanel(cfg),
                //         this.getCalendarPanel(cfg),
                //         this.getCedulaCPanel(cfg),
                //         //this.getRegisterPointPanel(cfg),
                //         Ext._create('Ext.Panel', {
                //             flex: 0.5,
                //             margins: `0 ${this.GAP} ${this.GAP} 0`,
                //             bodyStyle: {
                //                 padding: this.GAP,
                //                 backgroundColor: '#00000000',
                //                 border: 'none'
                //             },
                //         }),
                //         // this.getComprovanteRendimentosPanel(cfg),
                //     ],
                // },
            ],
        });

        return this._reportContainer;

    },

    getUserInfoContainer: function (cfg) {
        if (this._userInfoContainer) {
            return this._userInfoContainer;
        }

        this._userInfoContainer = Ext._create('Ext.Container', {
            layout: {
                type: 'vbox',
                align: 'stretch',
                padding: `${this.GAP} ${this.GAP} ${this.GAP} 0`,
            },
            width: 300,
            items: [
                this.getUserInfoPanel(cfg),
            ],
            listeners: {
                scope: this,
                hide: function (container) {
                    this.doLayout();
                },
                show: function (container) {
                    this.doLayout();
                },
            }
        });

        return this._userInfoContainer;
    },

    getEmployeePortalContainer: function (cfg) {
        if (this._employeePortalContainer) {
            return this._employeePortalContainer;
        }

        this._employeePortalContainer = Ext._create('Ext.Container', {
            layout: {
                type: 'vbox',
                align: 'stretch',
                padding: `${this.GAP} 0 ${this.GAP} ${this.GAP}`,
            },
            hidden: true,
            width: 300,
            items: [
                this.getEmployeePortalPanel(cfg),
            ],
            listeners: {
                scope: this,
                show: function (container) {
                    this.doLayout();
                },
            }
        });

        return this._employeePortalContainer;
    },

    getContainers: function (cfg) {
        if (this._containers) {
            return this._containers;
        }

        this._containers = [
            // this.getEmployeePortalContainer(cfg),
            // {
            //     xtype: 'container',
            //     layout: {
            //         type: 'vbox',
            //         align: 'stretch',
            //         padding: `${this.GAP} 0 ${this.GAP} ${this.GAP}`,
            //     },
            //     width: 375,
            //     items: [
            //         this.getPendentWorkPanel(cfg),
            //         this.getManualPanel(cfg),
            //     ],
            // },
            this.getUserInfoContainer(cfg),
            {
                xtype: 'container',
                flex: 1,
                layout: {
                    type: 'vbox',
                    align: 'stretch',
                    padding: `${this.GAP} ${this.GAP} ${this.GAP} ${this.GAP}`,
                },
                items: [
                    this.getReportContainer(cfg),
                    Ext._create('Ext.Panel', {
                        flex: 0.5,
                        bodyStyle: {
                            backgroundColor: '#00000000',
                            border: 'none'
                        },

                    
                    }),
                ],
            },
            
        ];

        return this._containers;
    },

    _resizeEvent: function (tbPanel, adjWidth, adjHeight, rawWidth, rawHeight) {
        // 1167 seria a largura mínima de tolerância para
        // visualização dos painéis de relatórios
        if (adjWidth < 1167) {
            this.getUserInfoContainer().isVisible() && this.getUserInfoContainer().hide();
        } else {
            !this.getUserInfoContainer().isVisible() && this.getUserInfoContainer().show();
        }
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            layout: {
                type: 'hbox',
                align: 'stretch',
            },
            style: {
                backgroundColor: this.BACKGROUND_COLOR,
            },
            defaults: {
                style: {
                    backgroundColor: this.BACKGROUND_COLOR,
                },
            },
            items: this.getContainers(cfg),
            listeners: {
                scope: this,
                resize: this._resizeEvent,
            }
        });

        core.dashboard.Container.superclass.constructor.call(this, cfg);

        // Recarrega o grid a cada 30 segundos
        var self = this;
        Ext.TaskMgr.start({
            interval: (600 * 1000),
            run: function () {
                self.getPendentWorkGrid().getStore().reload();
            }
        });
    },
});
