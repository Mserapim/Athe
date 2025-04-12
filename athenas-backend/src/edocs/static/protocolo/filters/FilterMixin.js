Ext._define('edocs.protocolo.filters.FilterMixin', {

    interestedFilter: function () {
        if (!this._interestedFilter) {
            this._interestedFilter = Ext._create('Ext.menu.Item', {
                text: 'Por Interessado',
                scope: this,
                handler: function () {
                    Ext._create('edocs.protocolo.filters.InterestedWindow', {
                        grid: this,
                        filterProperties: [
                            { property: 'protocolo__interessado', stage: 102 }
                        ]
                    }).show();
                }
            });
        }

        return this._interestedFilter;
    },

    removeInterestedFilter: function () {
        this.removeFilterProperty('protocolo__interessado', 102, false);
    },

    senderFilter: function () {
        if (!this._senderFilter) {
            this._senderFilter = Ext._create('Ext.menu.Item', {
                text: 'Por remetente',
                scope: this,
                handler: function() {
                    Ext._create('edocs.protocolo.filters.SendedByWindow', {
                        grid: this,
                        filterProperties: [
                            {property: 'servidor_origem', stage: 103}
                        ]
                    }).show();
                }
            });
        }

        return this._senderFilter;
    },

    removeSenderFilter: function () {
        this.removeFilterProperty('servidor_origem', 103, false);
    },

    originFilter: function () {
        if (!this._originFilter) {
            this._originFilter = Ext._create('Ext.menu.Item', {
                text: 'Por origem (Pessoa ou Local)',
                scope: this,
                handler: function () {
                    Ext._create('edocs.protocolo.filters.OriginWindow', {
                        grid: this,
                        filterProperties: [
                            { property: 'servidor_origem', stage: 104 },
                            { property: 'lotacao_origem', stage: 104 }
                        ]
                    }).show();
                }
            });
        }

        return this._originFilter;
    },

    removeOriginFilter: function () {
        this.removeFilterProperty('servidor_origem', 104, false);
        this.removeFilterProperty('lotacao_origem', 104, false);
    },

    destinationFilter: function () {
        if (!this._destinationFilter) {
            this._destinationFilter = Ext._create('Ext.menu.Item', {
                text: 'Por destino (Pessoa ou Local)',
                scope: this,
                handler: function() {
                    Ext._create('edocs.protocolo.filters.DestinationWindow', {
                        grid: this,
                        filterProperties: [
                            {property: 'servidor_destino', stage: 105},
                            {property: 'lotacao_destino', stage: 105}
                        ]
                    }).show();
                }
            });
        }

        return this._destinationFilter;
    },

    removeDestinationFilter: function () {
        this.removeFilterProperty('servidor_destino', 105, false);
        this.removeFilterProperty('lotacao_destino', 105, false);
    },

    sendDateFilter: function () {
        if (!this._sendDateFilter) {
            this._sendDateFilter = Ext._create('Ext.menu.Item', {
                text: 'Por data de encaminhamento',
                scope: this,
                handler: function () {
                    Ext._create('edocs.protocolo.filters.SendDateWindow', {
                        grid: this,
                        filterProperties: [
                            { property: 'data_encaminhamento__gte', stage: 106 },
                            { property: 'data_encaminhamento__lte', stage: 107 }
                        ]
                    }).show();
                }
            });
        }

        return this._sendDateFilter;
    },

    removeSendDateFilter: function () {
        this.removeFilterProperty('data_encaminhamento__gte', 106, false);
        this.removeFilterProperty('data_encaminhamento__lte', 107, false);
    },

    specieFilter: function () {
        if (!this._specieFilter) {
            this._specieFilter = Ext._create('Ext.menu.Item', {
                text: 'Por espécie do documento',
                scope: this,
                handler: function () {
                    Ext._create('edocs.protocolo.filters.SpecieWindow', {
                        grid: this,
                        filterProperties: [
                            { property: 'protocolo__tipo_documento', stage: 108 }
                        ]
                    }).show();
                }
            });
        }

        return this._specieFilter;
    },

    removeSpecieFilter: function () {
        this.removeFilterProperty('protocolo__tipo_documento', 108, false);
    },

    notReceivedFilter: function () {
        if (!this._notReceivedFilter) {
            this._notReceivedFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Somente as não recebidas',
                checked: false,
                scope: this,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function (item, checked) {
                        if (checked)
                            this.addFilterProperty('data_recebimento__isnull', 'on', 109);
                        else
                            this.removeFilterProperty('data_recebimento__isnull', 109);
                    }
                }
            });
        }

        return this._notReceivedFilter;
    },

    removeNotReceivedFilter: function () {
        this.removeFilterProperty('data_recebimento__isnull', 109, false);
    },

    urgentFilter: function () {
        if (!this._urgentFilter) {
            this._urgentFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Somente marcado como Urgente',
                checked: false,
                scope: this,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function (item, checked) {
                        if (checked)
                            this.addFilterProperty('urgente', 'on', 110);
                        else
                            this.removeFilterProperty('urgente', 110);
                    }
                }
            });
        }

        return this._urgentFilter;
    },

    removeUrgentFilter: function () {
        this.removeFilterProperty('urgente', 110, false);
    },

    confidentialFilter: function() {
        if (!this._confidentialFilter) {
            this._confidentialFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Somente marcado como Sigiloso',
                checked: false,
                scope: this,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function (item, checked) {
                        if(checked)
                            this.addFilterProperty('protocolo__sigiloso', 'true', 111);
                        else
                            this.removeFilterProperty('protocolo__sigiloso', 111);
                    }
                }
            });
        }

        return this._confidentialFilter;
    },

    removeConfidentialFilter: function () {
        this.removeFilterProperty('protocolo__sigiloso', 111, false);
    },

    electronicFilter: function () {
        if (!this._electronicFilter) {
            this._electronicFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Somente enviado por meio eletrônico',
                checked: false,
                scope: this,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function (item, checked) {
                        if (checked)
                            this.addFilterProperty('physical', 'off', 112);
                        else
                            this.removeFilterProperty('physical', 112);
                    }
                }
            });
        }

        return this._electronicFilter;
    },

    removeElectronicFilter: function () {
        this.removeFilterProperty('physical', 112, false);
    },

    physicalFilter: function () {
        if (!this._physicalFilter) {
            this._physicalFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Somente enviado por meio físico e eletrônico',
                checked: false,
                scope: this,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function (item, checked) {
                        if (checked)
                            this.addFilterProperty('physical', 'on', 112);
                        else
                            this.removeFilterProperty('physical', 112);
                    }
                }
            });
        }

        return this._physicalFilter;
    },

    withWorkflowFilter: function () {
        if (!this._withWorkflowFilter) {
            this._withWorkflowFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Mostrar documentos controlados',
                checked: false,
                scope: this,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function (item, checked) {
                        if (checked)
                            this.removeFilterProperty('with_workflow', 101);
                        else
                            this.setFilterProperty('with_workflow', 'off', 101);
                    }
                }
            });
        }

        return this._withWorkflowFilter;
    },
});