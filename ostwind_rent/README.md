        <!-- <field name="type">ostwind_rent_kanban_view</field> -->
    <record model="ir.ui.view" id="ostwind_rent_kanban_view">
        <field name="name">Ostwind Rent Kanban</field>
        <field name="model">ostwind.rent.object</field>
        <field name="type">kanban</field>
        <field name="arch" type="xml">
            <kanban>
                <templates>
                    <t t-name="kanban-box">
                        <div class="oe_resource_vignette">
                            <div class="oe_resource_image">
                                <a type="edit"><img alt="" t-att-src="kanban_image('object.name', 'photo', record.id.value)" class="oe_resource_picture"/></a>
                            </div>
                            <div class="oe_resource_details">
                                <ul>
                                   <li><field name="name"/></li>
                                   <li><field name="property_type"/></li>
                                </ul> 
                            </div>
                        </div>                       
                    </t>
                </templates>
            </kanban>
        </field>
    </record>


